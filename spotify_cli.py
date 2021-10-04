"""A CLI app for interacting with Spotify. It's a work in progress, so please be patient."""

import sys
from typing import List, Tuple
from itertools import zip_longest

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
    Edit,
)

# Allow arguments to be piped in via stdin
if __name__ == "__main__" and not sys.stdin.isatty():
    piped_arguments = sys.stdin.readline().rstrip("\n").split(" ")
    if len(piped_arguments) > 0:
        sys.argv.extend(piped_arguments)

spot = SpotipySpotifyFacade(output_object=typer.echo)
app = typer.Typer()
edit_app = typer.Typer()
app.add_typer(edit_app, name="edit", help=Edit.help)


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
    Create a new playlist.
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
        ...,
        help="Item type of collection to list. Supported types: playlist, album, track, artist, show, episode",
    ),
    limit: int = typer.Option(10, help="TODO: Add help"),
    offset: int = typer.Option(0, help="TODO: Add help"),
    retrieve_all: bool = typer.Option(False, help="TODO: Add help"),
):
    """
    List out items you have saved/followed.
    """
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


@edit_app.command(no_args_is_help=True)
def add(
    playlist_id: str = typer.Argument(
        ..., help="ID of playlist to add tracks to"
    ),
    track_ids: List[str] = typer.Argument(
        ...,
        help=Edit.Add.track_ids_help,
    ),
    insert_at: str = typer.Option(
        None, "--insert-at", "-i", help=Edit.Add.insert_at_help
    ),
    add_if_unique: bool = typer.Option(
        False,
        "--add-if-unique/--add-if-dupe",
        "-u/-U",
        help=Edit.Add.unique_help,
    ),
):
    """
    Add tracks to a playlist you own or are a collaborator on.
    """
    collection = spot.get_item("playlist", playlist_id)

    if insert_at is None:
        insert_at = [[None]] * len(track_ids)
    else:
        insert_at = [
            [int(n) for n in tk.split(",")]
            for tk in insert_at.rstrip().split(";")
        ]

    for track_id, index_list in zip_longest(
        track_ids, insert_at, fillvalue=[None]
    ):
        item = spot.get_item("track", track_id)
        if add_if_unique and collection.contains(item):
            typer.echo(Edit.Add.not_unique)
            continue

        for index in index_list:
            position = index
            collection.add(item, position=position)


@edit_app.command(no_args_is_help=True)
def remove(
    playlist_id: str = typer.Argument(
        ..., help="ID of playlist to add tracks to"
    ),
    track_ids: List[str] = typer.Argument(
        ...,
        help=Edit.Remove.track_ids_help,
    ),
    all: bool = typer.Option(False, "--all", "-a", help=Edit.Remove.all_help),
    specific: str = typer.Option(
        None, "--specific", "-s", help=Edit.Remove.specific_help
    ),
    offset: Tuple[int, int] = typer.Option(
        (0, -1), "--offset", "-o", help=Edit.Remove.offset_help
    ),
    count: int = typer.Option(1, "--count", "-c", help=Edit.Remove.count_help),
):
    """
    Remove tracks from a playlist you own, or are a collaborator on
    """
    collection = spot.get_item("playlist", playlist_id)

    if specific is None:
        specific = []
    else:
        specific = [
            [int(n) for n in tk.split(",") if tk.strip() != "..."]
            for tk in specific.rstrip().split(";")
        ]

    items = [spot.get_item("track", track_id) for track_id in track_ids]
    collection.remove(
        items, positions=specific, all=all, offset=offset, count=count
    )


@edit_app.command(no_args_is_help=True)
def details(
    playlist_id: str = typer.Argument(..., help="ID of playlist to edit"),
    name: str = typer.Option(None, "--name", "-n", help=Edit.Details.name_help),
    public: bool = typer.Option(
        None, "--public", "-P", help=Edit.Details.public_help
    ),
    collaborative: bool = typer.Option(
        None, "--collaborative", "-c", help=Edit.Details.collab_help
    ),
    description: str = typer.Option(
        None, "--description", "-d", help=Edit.Details.desc_help
    ),
):
    """
    Modify the details of playlist you own, or you that you are a collaborator on
    """
    playlist = spot.get_item("playlist", playlist_id)
    playlist.change_details(
        name=name,
        public=public,
        collaborative=collaborative,
        description=description,
    )


if __name__ == "__main__":
    app()
