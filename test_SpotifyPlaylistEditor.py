import typer 
import pytest 
import spotipy
from time import sleep

from SpotifyUtils import *
from spotipy.oauth2 import SpotifyOAuth
from typer.testing import CliRunner
from SpotifyPlaylistEditor import sp, app

runner = CliRunner()

#scope = "playlist-modify-private playlist-read-private"
#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# class TestCreate:
#     def test_name_clash_no_force():
#         result = runner.invoke(app, ["Test_Playlist_Name"])
#         assert result.exit_code == 0
#         assert "(Not Yet Implemented) Playlist 'Test_Playlist_Name'." in result.stdout

class TestDelete:
    def test_delete_no_force_cancled(self):        
        test_playlist_name = "TEST_PLAYLIST"
        result = runner.invoke(app, ["delete", test_playlist_name], input="n\n")
        assert result.exit_code == 0
        assert "Operation cancelled" in result.stdout

    def test_delete_no_force_approved(self):
        test_playlist_name = "TEST123"
        pl_id = create_playlist(sp, test_playlist_name)
        sleep(3)

        result = runner.invoke(app, ["delete", test_playlist_name], input="y\n")
        print(result.stdout)
        assert result.exit_code == 0
        assert f"Deleting Playlist: {test_playlist_name}" in result.stdout
        #assert check_exists(sp, pl_id) == False