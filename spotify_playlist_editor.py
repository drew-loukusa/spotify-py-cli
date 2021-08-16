"""A CLI app for managing your Spotify playlists. It's not very good yet, so please be patient."""

import sys
import textwrap
import typer
import spotipy
from decouple import config
from spotipy.oauth2 import SpotifyOAuth
import spotify_utils
from app_strings import General, Create, Search, Delete
from dummy_spotipy import DummySpotipy


SCOPE = "playlist-modify-private \
    playlist-read-private \
    playlist-read-collaborative \
    playlist-modify-public"
USE_DUMMY_WRAPPER = config("USE_DUMMY_WRAPPER", cast=bool, default=False)
SPOTIPY_CLIENT_ID = config("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = config("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = config("SPOTIPY_REDIRECT_URI")

sp = (
    DummySpotipy()
    if USE_DUMMY_WRAPPER
    else spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE,
        )
    )
)
app = typer.Typer()


@app.callback()
def callback():
    """
    A CLI app for managing your Spotify playlists.
    It's not very good yet, so please be patient.
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
    playlist = spotify_utils.get_playlist(sp, pl_name=name)
    name_exists = playlist is not None

    if not name_exists or force:
        spotify_utils.create_playlist(
            sp,
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

# TODO: Caching? To reduce number of pings to api
# TODO: add a "follow" command
# TODO: Before I can add a follow command, I need to implement searching through PUBLIC playlists
#       I need to update 'search' to search:
#           > Just a user's followed + created, playlists
#           > Public playlists
#           Add a flag to do this. Default should be...?
# Use:
# user_playlist_is_following(playlist_owner_id, playlist_id, user_ids)
# user_playlist_follow_playlist(playlist_owner_id, playlist_id)


@app.command()
def delete(
    name: str = typer.Argument(""),
    pl_id: str = typer.Option("", "--id", help=Delete.id_help),
    no_prompt: bool = typer.Option(
        False,
        "--no-prompt",
        help=Delete.no_prompt_help,
    ),
    delete_all: bool = typer.Option(False, "--all", help=Delete.all_help),
):
    """
    Delete (unfollow) a playlist from your library.
    """
    if name == "" and pl_id == "":
        typer.echo(Delete.specify_name_or_id)
        sys.exit(1)

    # Retrieve any playlists matching 'name' or 'pl_id'
    playlists = (
        spotify_utils.get_playlist(sp, pl_id=pl_id)
        if pl_id != ""
        else spotify_utils.get_playlist(sp, pl_name=name)
    )

    # Report how many playlist were found matching 'name' if name was used
    if pl_id == "" and playlists is not None:
        typer.echo(General.num_playlists_found.format(len(playlists), name))

        # If there is more than one playlist with the same name, list them out
        if len(playlists) > 1:
            for playlist in playlists:
                cur_name, cur_id, = (
                    playlist["name"],
                    playlist["id"],
                )
                print(f"{cur_name}, ID: {cur_id}")

    # Exit if there are duplicate playlist names and the right flags are not present
    if playlists is not None and len(playlists) > 1 and not (delete_all and no_prompt):
        typer.echo(Delete.duplicates_found.format(name))
        sys.exit(0)

    # Exit if the name or id given does not match any given playlist
    label = f"with name: '{name}'" if pl_id == "" else f"with id: '{pl_id}'"
    if playlists is None:
        typer.echo(General.playlist_DNE.format(label))
        typer.echo(General.operation_canceled)
        sys.exit(1)

    # If '--no-prompt' was not used, confirm delete with user
    confirm_delete = False
    if not no_prompt:
        confirm_delete = typer.confirm(text=Delete.confirm_delete.format(label))
    else:
        confirm_delete = True

    if confirm_delete:
        pl_name = None if name == "" else name
        pl_id = None if pl_id == "" else pl_id
        if playlists is not None and len(playlists) == 1:
            pl_id = playlists[0]["id"]
            pl_name = playlists[0]["name"]

        if delete_all:
            spotify_utils.delete_all(sp, pl_name=name)
            typer.echo(Delete.deleted_all.format(pl_name))
        else:
            spotify_utils.delete_playlist(sp, pl_id)
            typer.echo(Delete.deleted_playlist.format(pl_name, pl_id))
        sys.exit(0)

    typer.echo(General.operation_canceled)


@app.command()
def search(
    name: str = typer.Argument(""),
    public: bool = typer.Option(False, help=Search.public_help),
    limit: int = typer.Option(10, help=Search.limit_help),
    market: str = typer.Option("", help=Search.market_help),
):
    """
    Search through playlists you follow.
    Don't provide a name and this command will list all playlists you follow.

    Can also search public playlists with '--public'
    """
    if name == "":
        typer.echo(Search.listing_all)
        spotify_utils.list_playlists(sp)
    elif not public:
        playlists = spotify_utils.get_playlist(sp, name)
        if playlists is None:
            typer.echo(Search.playlist_DNE.format(name))
            sys.exit(1)
        else:
            typer.echo(General.num_playlists_found.format(len(playlists), name))
            for playlist in playlists:
                pl_name, pid, desc = (
                    playlist["name"],
                    playlist["id"],
                    playlist["description"],
                )
                typer.echo(Search.show_info.format(pl_name, pid, desc))
    else:
        typer.echo(Search.search_public)

        playlists = spotify_utils.search_public_playlist(
            sp, name, limit=limit, market=market
        )

        print(f"Found {len(playlists)} playlists matching the search query: '{name}'")
        for playlist in playlists:
            print("-----------------------")
            print(f"Name:\t\t{playlist['name']}")

            # TODO: Print user created playlists, and playlists user follows like this too
            desc = playlist["description"]
            wrapped_desc = textwrap.wrap(
                "Description:\t" + desc,
                width=64,
                initial_indent="",
                subsequent_indent="\t\t",
            )
            for line in wrapped_desc:
                print(line)

            print(f"Owner:\t\t{playlist['owner']['display_name']}")
            print(f"Track count:\t{playlist['tracks']['total']}")

            print(f"Playlist id:\t{playlist['id']}")
            print(f"Owner id:\t{playlist['owner']['id']}")
            print(f"Url: {playlist['external_urls']['spotify']}")


if __name__ == "__main__":
    app()
