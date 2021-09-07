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
    name = spot.follow_item(item_type=item_type, item_id=item_id)
    typer.echo(Follow.followed.format(item_type, name, item_id))
    sys.exit(0)


@app.command()
def unfollow(
    name: str = typer.Argument(""),
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

    # Retrieve any playlists matching 'name' or 'pl_id'
    playlists = spot.get_playlist(pl_name=name, pl_id=item_id)

    # Report how many playlist were found matching 'name' if name was used
    if item_id == "" and playlists is not None:
        typer.echo(General.num_items_found.format(len(playlists), name))

        # If there is more than one playlist with the same name, list them out
        if len(playlists) > 1:
            spot.print_playlists(typer.echo, playlists)

    # Exit if there are duplicate playlist names
    # User will have to specify with ID which item to unfollow
    if playlists is not None and len(playlists) > 1:
        typer.echo(Unfollow.dupes_found.format(name))
        sys.exit(0)

    # Exit if the name or id given does not match any given playlist
    spec_type = "name" if item_id == "" else "id"
    specifier = name if item_id == "" else item_id
    if playlists is None:
        typer.echo(General.item_DNE.format(spec_type, specifier))
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
        pl_name = None if name == "" else name
        item_id = None if item_id == "" else item_id
        if playlists is not None and len(playlists) == 1:
            item_id = playlists[0]["id"]
            pl_name = playlists[0]["name"]
        spot.unfollow_playlist(item_id)
        typer.echo(Unfollow.unfollowed_item.format(pl_name, item_id))
        sys.exit(0)

    typer.echo(General.op_canceled)


@app.command()
def search(
    name: str = typer.Argument(""),
    public: bool = typer.Option(False, help=Search.public_help),
    limit: int = typer.Option(10, help=Search.limit_help),
    market: str = typer.Option(None, help=Search.market_help),
):
    """
    Search through playlists you follow.
    Don't provide a name and this command will list all playlists you follow.

    Can also search public playlists with '--public'
    """
    if name == "":
        typer.echo(Search.list_all)
        spot.print_playlists(
            print_func=typer.echo, playlists=spot.get_user_playlists()
        )

    # Search through user created playlists, and user followed playlists
    elif not public:
        playlists = spot.get_playlist(name)
        if playlists is None:
            typer.echo(General.not_found.format(name))
            sys.exit(1)
        else:
            typer.echo(General.num_items_found.format(len(playlists), name))
            spot.print_playlists(print_func=typer.echo, playlists=playlists)

    # Search through all public playlists
    else:
        typer.echo(Search.search_pub)
        playlists = spot.search_public_playlist(
            query=name, limit=limit, market=market
        )

        typer.echo(Search.num_public.format(len(playlists), name))
        spot.print_playlists(typer.echo, playlists)


if __name__ == "__main__":
    app()
