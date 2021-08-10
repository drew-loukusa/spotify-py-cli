import typer 
import spotipy
from SpotifyUtils import *
from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-modify-private playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

app = typer.Typer()


@app.command()
def create(name: str):
    typer.echo(f"(Not Yet Implemented) Playlist '{name}'.")

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