"""A CLI app for interacting with Spotify. It's a work in progress, so please be patient."""
import sys
import typer
from spotipy_facade import SpotipySpotifyFacade
from app_strings import General, Create, Search, Follow, Unfollow


spot = SpotipySpotifyFacade()
app = typer.Typer()


@app.callback()
def callback():
    """
    A CLI app for interacting with Spotify. It's a work in progress, so please be patient.
    """


@app.command()
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


@app.command()
def follow(
    item_type: str = typer.Argument(
        ..., help="Item type to follow: 'playlist' or 'artist'"
    ),
    item_id: str = typer.Argument(..., help=Follow.id_help),
):
    """Follow a followable item (playlist or artist)"""
    item = spot.get_followable_instance(item_type, item_id)
    name = item.name
    item.follow()
    typer.echo(Follow.followed.format(item_type, name, item_id))
    sys.exit(0)


@app.command()
def unfollow(
    item_type: str = typer.Argument(
        ..., help="Item type to follow: 'playlist' or 'artist'"
    ),
    name: str = typer.Argument("", help=""),
    item_id: str = typer.Option("", "--id", help=Unfollow.id_help),
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
    if name == "" and item_id == "":
        typer.echo(General.spec_name_id)
        sys.exit(1)

    # Retrieve any items matching 'name' or 'pl_id'
    items = spot.get_followed_item(
        item_type=item_type, item_name=name, item_id=item_id
    )

    # Report how many items were found matching 'name' if name was used
    if item_id == "" and items is not None:
        typer.echo(General.num_items_found.format(len(items), name))

        # If there is more than one item with the same name, list them out
        if len(items) > 1:
            spot.print_items(item_type, typer.echo, items)

    # Exit if there are duplicate item names
    # User will have to specify with ID which item to unfollow
    if items is not None and len(items) > 1:
        typer.echo(Unfollow.dupes_found.format(name))
        sys.exit(0)

    # Exit if the name or id given does not match any given item
    spec_type = "name" if item_id == "" else "id"
    specifier = name if item_id == "" else item_id
    if items is None:
        typer.echo(General.item_DNE.format(item_type, spec_type, specifier))
        typer.echo(General.op_canceled)
        sys.exit(1)

    # If '--no-prompt' was not used, confirm Unfollow with user
    confirm_Unfollow = False
    if not no_prompt:
        confirm_Unfollow = typer.confirm(
            text=Unfollow.confirm.format(spec_type, specifier)
        )
    else:
        confirm_Unfollow = True

    if confirm_Unfollow:
        item_name, item_id = items[0].name, items[0].id
        items[0].unfollow()
        typer.echo(Unfollow.unfollowed_item.format(item_name, item_id))
        sys.exit(0)

    typer.echo(General.op_canceled)


@app.command()
def search(
    # item_type: str = typer.Argument(
    #     ..., help="Item type to follow: 'playlist' or 'artist'"
    # ),
    query: str = typer.Argument(""),
    user: bool = typer.Option(False, help=Search.user_help),
    limit: int = typer.Option(10, help=Search.limit_help),
    market: str = typer.Option(None, help=Search.market_help),
):
    """
    Search for followalable items.

    To limit search to just items that a user follows use the '--user' flag
    Don't provide a name and this command will list all playlists you follow.
    """

    # TODO: REMOVE THIS
    item_type = "playlist"

    if query == "" and user:
        typer.echo(Search.list_all)
        spot.print_items(
            item_type=item_type,
            print_func=typer.echo,
            items=spot.get_user_items(item_type),
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
            spot.print_playlists(print_func=typer.echo, playlists=items)

    # Search through all public playlists
    else:
        typer.echo(Search.search_pub)
        items = spot.search_public_playlist(
            query=query, limit=limit, market=market
        )

        typer.echo(Search.num_items_found.format(len(items), query))
        spot.print_playlists(typer.echo, items)


if __name__ == "__main__":
    app()
