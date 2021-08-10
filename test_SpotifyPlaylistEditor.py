from time import sleep

from SpotifyUtils import *
from typer.testing import CliRunner
from SpotifyPlaylistEditor import sp, app

runner = CliRunner()

TEST_PL_NAME = "TEST_PL_NAME"
class TestCreate:
    def test_create_playlist(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME])
        assert result.exit_code == 0 
        assert "Playlist created." in result.stdout

        # Clean up 
        pl_id = get_pl_id_from_name(sp, TEST_PL_NAME)
        delete_playlist(sp, pl_id)

    def test_name_clash_no_force(self):
        create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME])
        assert result.exit_code == 0 
        assert "Playlist with that name already exists. \
            Please choose a diffrent name or use '--force' \
                to overwrite the existing list." in result.stdout
        
        # Clean up 
        pl_id = get_pl_id_from_name(sp, TEST_PL_NAME)
        delete_playlist(sp, pl_id)

    def test_name_clash_force(self):
        create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--force"])
        assert result.exit_code == 0 
        assert "Playlist Overwritten with new playlist." in result.stdout

        # Clean up 
        pl_id = get_pl_id_from_name(sp, TEST_PL_NAME)
        delete_playlist(sp, pl_id)

class TestDelete:
    def test_delete_no_force_cancled(self):      
        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="n\n")
        assert result.exit_code == 0
        assert "Operation cancelled" in result.stdout

    def test_delete_no_force_approved(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\n")
        print(result.stdout)
        assert result.exit_code == 0
        assert f"Deleting Playlist: {TEST_PL_NAME}" in result.stdout
        assert check_exists(sp, pl_id) == False