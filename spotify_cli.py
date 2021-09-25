"""A CLI app for interacting with Spotify. It's a work in progress, so please be patient."""

import sys

import typer

from spotipy_facade import SpotipySpotifyFacade
from app_strings import (
    General,
    Create,
    Listing,
    Search,
    Follow,
    Unfollow,
    Save,
    Unsave,
)


spot = SpotipySpotifyFacade(output_object=typer.echo)
app = typer.Typer()


@app.callback()
def callback():
    """
    A CLI app for interacting with Spotify. It's a work in progress, so please be patient.
    """


@app.command(no_args_is_help=True)
def create(
    name: str,
    desc: str = typer.Option("", help=Create.desc_help),
    public: bool = typer.Option(False, help=Create.public_help),
    collab: bool = typer.Option(False, help=Create.collab_help),
    force: bool = typer.Option(False, help=Create.force_help),
):
    """
    Creates a new playlist.
    """

    # Check if name is already in use
    playlist = spot.get_playlist(pl_name=name)
    name_exists = playlist is not None

    if not name_exists or force:
        spot.create_playlist(
            name=name,
            public=public,
            collaborative=collab,
            description=desc,
        )
        if name_exists:
            typer.echo(Create.dupe_created)
        else:
            typer.echo(Create.plist_created)
        typer.echo(Create.pub_status.format(public))
        typer.echo(Create.collab_status.format(collab))
        typer.echo(Create.desc_status.format(desc))

    else:
        typer.echo(Create.dupe_exist_no_f)


@app.command(no_args_is_help=True)
def follow(
    item_type: str = typer.Argument(
        ..., help="Item type to follow: 'playlist' or 'artist'"
    ),
    item_id: str = typer.Argument(..., help=Follow.id_help),
):
    """Follow a followable item"""

    item, collection = spot.get_item_and_collection(
        item_type=item_type, item_id=item_id
    )

    if item is not None and collection is not None:
        collection.add(item)
        typer.echo(Follow.followed.format(item_type, item.name, item_id))
        sys.exit(0)

    sys.exit(1)


@app.command(no_args_is_help=True)
def save(
    item_type: str = typer.Argument(
        ..., help="Item type to save: 'album', 'track', 'show', or 'episode'"
    ),
    item_id: str = typer.Argument(..., help=Follow.id_help),
):
    """Save a saveable item"""

    item, collection = spot.get_item_and_collection(
        item_type=item_type, item_id=item_id
    )

    if item is not None and collection is not None:
        collection.add(item)
        typer.echo(Save.saved.format(item_type, item.name, item_id))
        sys.exit(0)

    sys.exit(1)


@app.command(no_args_is_help=True)
def unfollow(
    item_type: str = typer.Argument(
        ..., help="Item type to follow: 'playlist' or 'artist'"
    ),
    item_id: str = typer.Argument(..., help=Unfollow.id_help),
    no_prompt: bool = typer.Option(
        False,
        "--no-prompt",
        help=Unfollow.no_prompt_help,
    ),
):
    """
    Unfollow an item; remove it from your library.
    This "deletes" playlists you've created.
    """
    # Retrieve item matching item_id
    item, collection = spot.get_item_and_collection(
        item_type=item_type, item_id=item_id
    )

    if item is None or collection is None:
        sys.exit(1)

    # If '--no-prompt' was not used, confirm Unfollow with user
    confirm_Unfollow = False
    if not no_prompt:
        confirm_Unfollow = typer.confirm(
            text=Unfollow.confirm.format(item_type, item.name, item_id)
        )
    else:
        confirm_Unfollow = True

    if confirm_Unfollow:
        collection.remove(item)
        typer.echo(Unfollow.unfollowed_item.format(item.name, item_id))
        sys.exit(0)

    typer.echo(General.op_canceled)


@app.command(no_args_is_help=True)
def unsave(
    item_type: str = typer.Argument(
        ..., help="Item type to unsave: 'album', 'track', 'show', or 'episode'"
    ),
    item_id: str = typer.Argument(..., help=Follow.id_help),
):
    """Unsave a saveable item"""

    item, collection = spot.get_item_and_collection(
        item_type=item_type, item_id=item_id
    )

    if item is not None and collection is not None:
        collection.remove(item)
        typer.echo(Unsave.unsaved.format(item_type, item.name, item_id))
        sys.exit(0)

    sys.exit(1)


@app.command(no_args_is_help=True)
def search(
    item_type: str = typer.Argument(
        ..., help="Item type to follow: 'playlist' or 'artist'"
    ),
    query: str = typer.Argument(""),
    user: bool = typer.Option(False, help=Search.user_help),
    limit: int = typer.Option(10, help=Search.limit_help),
    market: str = typer.Option(None, help=Search.market_help),
):
    """
    Search for items.

    To limit search to just items that a user follows use the '--user' flag
    Don't provide a name and this command will list all playlists you follow.
    """

    if query == "" and user:
        typer.echo(Search.list_all)
        spot.print_items(
            print_func=typer.echo,
            items=spot.get_followed_items(item_type),
        )
    elif query == "":
        typer.Exit(code=1)

    # Search through user created items, and user followed items
    elif user:
        items = spot.get_followed_item(item_type=item_type, item_name=query)
        if items is None:
            typer.echo(General.not_found.format(query))
            sys.exit(1)
        else:
            typer.echo(Search.num_items_found.format(len(items), query))
            spot.print_items(print_func=typer.echo, items=items)

    # Search through all public playlists
    else:
        typer.echo(Search.search_pub)
        items = spot.search_public(
            item_type, query, limit, offset=0, market=market
        )

        typer.echo(Search.num_items_found.format(len(items), query))
        spot.print_items(typer.echo, items)


@app.command(no_args_is_help=True)
def list(
    item_type: str = typer.Argument(
        ..., help="Item type of collection to list"
    ),
    limit: int = typer.Option(10, help="TODO: Add help"),
    offset: int = typer.Option(0, help="TODO: Add help"),
    retrieve_all: bool = typer.Option(False, help="TODO: Add help"),
):
    collection = spot.get_collection(item_type)
    if collection is None:
        typer.echo(f"Collection for type {item_type} does not exist")
        sys.exit(1)

    typer.echo(Listing.listing.format(item_type))
    if not retrieve_all:
        typer.echo(Listing.params.format(limit, offset))
    else:
        typer.echo(Listing.ret_all)
    for item in collection.items(
        limit=limit, offset=offset, retrieve_all=retrieve_all
    ):
        typer.echo(item)


if __name__ == "__main__":
    app()
