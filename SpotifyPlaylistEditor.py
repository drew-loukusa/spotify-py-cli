import os
from click.termui import confirm
import typer
import spotipy
from SpotifyUtils import *
from spotipy.oauth2 import SpotifyOAuth
from dummy_spotipy import DummySpotipy

scope = "playlist-modify-private playlist-read-private"
USE_DUMMY_WRAPPER = os.getenv("USE_DUMMY_WRAPPER")
sp = (
    DummySpotipy()
    if USE_DUMMY_WRAPPER == "True"
    else spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
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
    force: bool = typer.Option(False),
):
    # Check if name is already in use
    playlist = get_playlist(sp, pl_name=name)
    name_exists = True if playlist != None else False

    if force:
        create_playlist(sp, name)
        if name_exists:
            typer.echo("Playlist with duplicate name created.")
        else:
            typer.echo("Playlist created.")

    else:
        if not name_exists:
            create_playlist(sp, name)
            typer.echo("Playlist created.")
        else:
            typer.echo(
                "A playlist with that name already exists.\n"
                + "Choose a diffrent name or use '--force'"
                + "to create a playlist with the same name "
                + "as the existing playlist."
            )


@app.command()
def delete(
    name: str = typer.Argument(""),
    id: str = typer.Option("", help="Use id to specify playlist"),
    no_prompt: bool = typer.Option(
        False,
        "--no-prompt",
        help="Do not prompt user to confirm deletion. Will be ignored if NAME "
        + "is supplied and multiple playlists exist with the same name.\n"
        + "See '--all' for deleting multiple lists that share the same name.",
    ),
    all: bool = typer.Option(
        False,
        help="If multiple lists are found that share the same name, delete all. "
        + "Only has effect if used with --no-prompt.",
    ),
):
    if name == "" and id == "":
        typer.echo("You must specify NAME or ID")
        exit(1)

    playlists = (
        get_playlist(sp, pl_id=id) if id != "" else get_playlist(sp, pl_name=name)
    )

    if id == "" and playlists != None:
        typer.echo(f"{len(playlists)} playlist(s) found matching name {name}")
        if len(playlists) > 1:
            for playlist in playlists:
                pn, pid, = (
                    playlist["name"],
                    playlist["id"],
                )
                print(f"{pn}, ID: {pid}")

    if playlists != None and len(playlists) > 1 and not (all and no_prompt):
        typer.echo(
            f"Multiple playlists were found with name: {name}."
            + "\nPlease use '--no-prompt' with '--all' to "
            + "delete all, or specify with '--id' which playlist to delete."
        )
        exit(0)

    label = f"with name: '{name}'" if id == "" else f"with id: '{id}'"
    if playlists is None:
        typer.echo(f"Playlist {label} appears to not exist!")
        typer.echo("Operation cancelled")
        exit(1)

    confirm_delete = False
    if not no_prompt:
        confirm_delete = typer.confirm(
            text=f"Are you sure you want to delete the playlist {label}?"
        )
    else:
        confirm_delete = True

    if confirm_delete:
        pl_name = None if name == "" else name
        pl_id = None if id == "" else id
        if playlists != None and len(playlists) == 1:
            pl_id = playlists[0]["id"]
            pl_name = playlists[0]["name"]

        if all:
            delete_all(sp, pl_name=name)
            typer.echo(f"Deleted all playlists associated with name: {pl_name}")
        else:
            delete_playlist(sp, pl_id)
            typer.echo(f"Deleted playlist: {pl_name}, ID: {pl_id}")
        exit(0)

    else:
        typer.echo("Operation cancelled")


@app.command()
def search(name: str = typer.Argument("")):
    if name == "":
        typer.echo("No name provided, listing all playlists...")
        list_playlists(sp)
    else:
        playlists = get_playlist(sp, name)
        if playlists is None:
            typer.echo(f"Could not find {name} in user's playlists.")
            exit(1)
        else:
            typer.echo(f"{len(playlists)} playlist(s) found matching name {name}")
            for playlist in playlists:
                pn, pid, = (
                    playlist["name"],
                    playlist["id"],
                )
                print(f"{pn}, ID: {pid}")


if __name__ == "__main__":
    app()
