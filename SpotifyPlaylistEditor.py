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
        if name_exists:
            pl_id = playlist['id']
            delete_playlist(sp, pl_id)
        create_playlist(sp, name)
        typer.echo(f"Playlist Overwritten with new playlist.")
    else:
        if not name_exists:
            create_playlist(sp, name)
            typer.echo("Playlist created.")
        else:
            typer.echo(
                "Playlist with that name already exists. \
            Please choose a diffrent name or use '--force' \
                to overwrite the existing list."
            )


@app.command()
def delete(
    name: str,
    force: bool = typer.Option(
        ..., prompt=f"Are you sure you want to delete the playlist?"
    ),
):
    if force:
        playlist = get_playlist(sp, pl_name=name)
        pl_id = "" if playlist is None else playlist['id']

        if playlist is None:
            typer.echo(f"Playlist '{name}' could not be deleted as it appears to not exist!")
            exit(1)
            
        delete_playlist(sp, pl_id)
        typer.echo(f"Deleting Playlist: {name}")
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
    app()
