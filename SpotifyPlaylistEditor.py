import os
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
        #     pl_id = playlist["id"]
        #     delete_playlist(sp, pl_id)

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
        ...,
        "--no-prompt",
        help="Do prompt user to confirm delete.",
        prompt=f"Are you sure you want to delete the playlist?",
    ),
    all: bool = typer.Option(
        False,
        help="If multiple lists are found, delete all. Only has effect if used with --no-prompt.",
    ),
):
    if name == "" and id == "": 
        typer.echo("You must specify NAME or ID")
        exit(1)

    # person_name = typer.prompt("What's your name?")
    if no_prompt:
        playlists = (
            get_playlist(sp, pl_id=id) 
            if id != "" 
            else get_playlist(sp, pl_name=name)
        )
        if playlists is None:
            label = f"with name: '{name}'" if id == "" else f"with id: '{id}'"
            typer.echo(
                f"Playlist {label} could not be deleted as it appears to not exist!"
            )
            exit(1)

        pl_id = None if id == "" else id 
        if playlists != None and len(playlists) > 0:
            typer.echo(f"Multiple playlists were found with name: {name}")
        elif playlists != None and len(playlists) == 1:
            pl_id = playlists[0]["id"]

        delete_playlist(sp, pl_id)
        typer.echo(f"Deleted playlist: {name}")
    else:
        typer.echo("Operation cancelled")


@app.command()
def search(name: str = typer.Argument("")):
    if name == "":
        typer.echo("No name provided, listing all playlists...")
        list_playlists(sp)
    else:
        playlist = get_playlist(sp, name)
        if playlist is None:
            typer.echo(f"Could not find {name} in user's playlists.")
            exit(1)
        else:
            typer.echo(f"Found playlist {name}.")


if __name__ == "__main__":
    create_playlist(sp, "TEST123")
    app()
