import typer 
import spotipy
from SpotifyUtils import *
from spotipy.oauth2 import SpotifyOAuth
from dummy_spotipy import DummySpotipy

scope = "playlist-modify-private playlist-read-private"
sp = DummySpotipy()
#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
app = typer.Typer()


@app.command()
def create(
    name: str,
    force: bool = typer.Option(False),
):
    pl_id = get_pl_id_from_name(sp, name)
    name_exists = check_exists(sp, pl_id)
    if force:
        if name_exists:
            delete_playlist(sp, pl_id)
        create_playlist(sp, name)
        typer.echo(f"Playlist Overwritten with new playlist.")
    else:
        if not name_exists:
            create_playlist(sp, name)
            typer.echo("Playlist created.")
        else:
            typer.echo("Playlist with that name already exists. \
            Please choose a diffrent name or use '--force' \
                to overwrite the existing list.")

@app.command()
def delete(
    name: str,
    force: bool = typer.Option(..., prompt=f"Are you sure you want to delete the playlist?"),
):
    if force:
        pl_id = get_pl_id_from_name(sp, name)
        delete_playlist(sp, pl_id)
        typer.echo(f"Deleting Playlist: {name}")
    else:
        typer.echo("Operation cancelled")

if __name__ == "__main__":
    app()