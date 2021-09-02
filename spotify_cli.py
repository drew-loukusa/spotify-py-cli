"""A CLI app for interacting with Spotify. It's a work in progress, so please be patient."""

import sys
import spotipy
import typer
from decouple import config
from spotipy.oauth2 import SpotifyOAuth
from spotify_utils import SpotifyExtended
from app_strings import General, Create, Search, Follow, Unfollow

SCOPE = "playlist-modify-private \
    playlist-read-private \
    playlist-read-collaborative \
    playlist-modify-public"
SPOTIPY_CLIENT_ID = config("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = config("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = config("SPOTIPY_REDIRECT_URI")

# TODO: Caching? To reduce number of pings to api
# TODO: Improve handling of when api calls timeout or fail. I don't account for api calls timing out, at all? So...
#
sp = SpotifyExtended(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
    )
)

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
    collab: bool = typer.Option(False, "--collab", help=Create.collab_help),
    force: bool = typer.Option(False, help=Create.force_help),
):
    """
    Creates a new playlist.
    """

    # Check if name is already in use
    playlist = sp.get_playlist(pl_name=name)
    name_exists = playlist is not None

    if not name_exists or force:
        sp.create_playlist(
            name=name,
            public=public,
            collaborative=collab,
            description=desc,
        )
        if name_exists:
            typer.echo(Create.duplicate_created)
        else:
            typer.echo(Create.playlist_created)
        typer.echo(Create.pub_status.format(public))
        typer.echo(Create.collab_status.format(collab))
        typer.echo(Create.desc_status.format(desc))

    else:
        typer.echo(Create.dupe_exists_no_force)


@app.command()
def follow(pl_id: str = typer.Argument(..., help=Follow.id_help)):
    """Follow a playlist"""
    sp.current_user_follow_playlist(playlist_id=pl_id)
    name = sp.get_playlist(pl_id=pl_id)[0]["name"]
    typer.echo(Follow.followed.format(name, pl_id))
    sys.exit(0)


@app.command()
def unfollow(
    name: str = typer.Argument(""),
    pl_id: str = typer.Option("", "--id", help=Unfollow.id_help),
    no_prompt: bool = typer.Option(
        False,
        "--no-prompt",
        help=Unfollow.no_prompt_help,
    ),
    unfollow_all: bool = typer.Option(False, "--all", help=Unfollow.all_help),
):
    """
    Unfollow a playlist; remove it from your library.
    This "deletes" playlists you've created.
    """
    if name == "" and pl_id == "":
        typer.echo(General.specify_name_or_id)
        sys.exit(1)

    # Retrieve any playlists matching 'name' or 'pl_id'
    playlists = (
        sp.get_playlist(pl_id=pl_id) if pl_id != "" else sp.get_playlist(pl_name=name)
    )

    # Report how many playlist were found matching 'name' if name was used
    if pl_id == "" and playlists is not None:
        typer.echo(General.num_playlists_found.format(len(playlists), name))

        # If there is more than one playlist with the same name, list them out
        if len(playlists) > 1:
            sp.print_playlists(typer.echo, playlists)

    # Exit if there are duplicate playlist names and the right flags are not present
    if (
        playlists is not None
        and len(playlists) > 1
        and not (unfollow_all and no_prompt)
    ):
        typer.echo(Unfollow.duplicates_found.format(name))
        sys.exit(0)

    # Exit if the name or id given does not match any given playlist
    label = f"with name: '{name}'" if pl_id == "" else f"with id: '{pl_id}'"
    if playlists is None:
        typer.echo(General.playlist_DNE.format(label))
        typer.echo(General.operation_canceled)
        sys.exit(1)

    # If '--no-prompt' was not used, confirm Unfollow with user
    confirm_Unfollow = False
    if not no_prompt:
        confirm_Unfollow = typer.confirm(text=Unfollow.confirm_unfollow.format(label))
    else:
        confirm_Unfollow = True

    if confirm_Unfollow:
        pl_name = None if name == "" else name
        pl_id = None if pl_id == "" else pl_id
        if playlists is not None and len(playlists) == 1:
            pl_id = playlists[0]["id"]
            pl_name = playlists[0]["name"]

        if unfollow_all:
            sp.unfollow_all_pl(pl_name=name)
            typer.echo(Unfollow.unfollowed_all.format(pl_name))
        else:
            sp.unfollow_playlist(pl_id)
            typer.echo(Unfollow.unfollowed_playlist.format(pl_name, pl_id))
        sys.exit(0)

    typer.echo(General.operation_canceled)


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
        typer.echo(Search.listing_all)
        sp.print_playlists(typer.echo, sp.get_user_playlists())

    # Search through user created playlists, and user followed playlists
    elif not public:
        playlists = sp.get_playlist(name)
        if playlists is None:
            typer.echo(Search.playlist_DNE.format(name))
            sys.exit(1)
        else:
            typer.echo(General.num_playlists_found.format(len(playlists), name))
            sp.print_playlists(typer.echo, playlists)

    # Search through all public playlists
    else:
        typer.echo(Search.search_public)
        playlists = sp.search_public_playlist(name, limit=limit, market=market)

        typer.echo(Search.num_public.format(len(playlists), name))
        sp.print_playlists(typer.echo, playlists)


if __name__ == "__main__":
    app()
