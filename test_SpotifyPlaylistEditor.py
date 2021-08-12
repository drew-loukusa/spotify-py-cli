from time import sleep

from SpotifyUtils import *
from typer.testing import CliRunner
from SpotifyPlaylistEditor import sp, app

runner = CliRunner()

TEST_PL_NAME = "TEST_PL_NAME"


class TestCreate:
    def test_create_playlist(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME])

        # Clean up
        delete_all(sp, TEST_PL_NAME)

        assert result.exit_code == 0
        assert "Playlist created." in result.stdout

    def test_create_name_clash_no_force(self):
        create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME])

        # Clean up
        delete_all(sp, TEST_PL_NAME)

        assert result.exit_code == 0
        assert (
            "A playlist with that name already exists.\n"
            + "Choose a diffrent name or use '--force'"
            + "to create a playlist with the same name "
            + "as the existing playlist."
            in result.stdout
        )

    def test_create_name_clash_force(self):
        create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--force"])

        # Clean up
        delete_all(sp, TEST_PL_NAME)

        assert result.exit_code == 0
        assert "Playlist with duplicate name created." in result.stdout


class TestDelete:
    def test_delete_no_name_or_id(self):
        result = runner.invoke(app, ["delete", "--no-prompt"])
        assert result.exit_code == 1
        assert "You must specify NAME or ID" in result.stdout

    def test_delete_prompt_cancled(self):
        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="n\n")
        assert result.exit_code == 0
        assert "Operation cancelled" in result.stdout

    def test_delete_prompt_approved(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\n")
        pl_exists = check_exists(sp, pl_id)

        # Cleanup, if needed
        if pl_exists:
            delete_playlist(sp, pl_id)

        assert result.exit_code == 0
        assert f"Deleted playlist: {TEST_PL_NAME}" in result.stdout
        assert pl_exists == False

    def test_delete_by_id(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", "--id", pl_id], input="y\n")
        pl_exists = check_exists(sp, pl_id)

        # Cleanup, if needed
        if pl_exists:
            delete_playlist(sp, pl_id)

        assert result.exit_code == 0
        assert f"Deleted playlist: {TEST_PL_NAME} with id {pl_id}" in result.stdout
        assert pl_exists == False

    def test_delete_no_prompt(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", "--no-prompt", TEST_PL_NAME])
        pl_exists = check_exists(sp, pl_id)

        # Cleanup, if needed
        if pl_exists:
            delete_playlist(sp, pl_id)

        assert result.exit_code == 0
        assert f"Deleted playlist: {TEST_PL_NAME}" in result.stdout
        assert pl_exists == False

    def test_delete_playlist_DNE(self):
        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\n")
        assert result.exit_code == 1
        assert (
            f"Playlist with name: '{TEST_PL_NAME}' could not be deleted as it appears to not exist!"
            in result.stdout
        )

    def test_delete_name_clash_prompt_select_single(self):
        """
        Test deleting when multiple playlists share the same name.
        Prompt user if they want to proceed.
        User selects one playlist to be deleted.
        """
        pl_id1 = create_playlist(sp, TEST_PL_NAME)
        pl_id2 = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\n1\n")
        pl_exists = check_exists(sp, pl_id1)

        # Cleanup
        delete_playlist(sp, pl_id2)
        if pl_exists:
            delete_playlist(sp, pl_id1)

        assert result.exit_code == 0
        assert (
            f"Multiple playlists were found with name: {TEST_PL_NAME}" in result.stdout
        )
        assert pl_exists == False

    def test_delete_name_clash_prompt_select_all(self):
        """
        Test deleting multiple playlists.
        Prompt user if they want to proceed.
        User selects all playlists to be deleted.
        """
        pl_id1 = create_playlist(sp, TEST_PL_NAME)
        pl_id2 = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\nall\n")
        pl1_exists = check_exists(sp, pl_id1)
        pl2_exists = check_exists(sp, pl_id1)

        # Cleanup, if needed
        if pl1_exists:
            delete_playlist(sp, pl_id1)
        if pl2_exists:
            delete_playlist(sp, pl_id2)

        assert result.exit_code == 0
        assert (
            f"Multiple playlists were found with name: {TEST_PL_NAME}" in result.stdout
        )
        assert pl1_exists == False
        assert pl2_exists == False

    def test_delete_name_clash_no_prompt_all(self):
        """
        Test deleting multiple playlists.
        Skip prompt with --no-prompt
        Use --all flag to delete all.
        """
        pl_id1 = create_playlist(sp, TEST_PL_NAME)
        pl_id2 = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", "--no-prompt", "--all", TEST_PL_NAME])
        pl1_exists = check_exists(sp, pl_id1)
        pl2_exists = check_exists(sp, pl_id1)

        # Cleanup, if needed
        if pl1_exists:
            delete_playlist(sp, pl_id1)
        if pl2_exists:
            delete_playlist(sp, pl_id2)

        assert result.exit_code == 0
        assert (
            f"Multiple playlists were found with name: {TEST_PL_NAME}" in result.stdout
        )
        assert pl1_exists == False
        assert pl2_exists == False

    def test_delete_name_clash_no_prompt_no_all(self):
        """
        Test deleting when multiple lists exist with same name and
        --no-prompt flag was used ()
        If multiple lists exist with given name, cli does not know
        which to delete. It should exit with code 1, and tell user.
        """
        pl_id1 = create_playlist(sp, TEST_PL_NAME)
        pl_id2 = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", "--no-prompt", TEST_PL_NAME])

        # Cleanup
        delete_playlist(sp, pl_id1)
        delete_playlist(sp, pl_id2)

        assert result.exit_code == 0
        assert (
            f"Multiple playlists were found with name: {TEST_PL_NAME} and '--no-prompt' was used. Please use '--no-prompt' with '--all' to delete all, run delete without '--no-prompt' to select the list to be deleted, or specfiy with '--id' which playlist to delete."
            in result.stdout
        )


# class TestSearch:
#     def test_search_no_name_provided(self):
#         result = runner.invoke(app, ["search"])
#         assert result.exit_code == 0
#         assert "No name provided, listing all playlists..." in result.stdout

#     def test_search_name_provided_and_playlist_exists(self):
#         create_playlist(sp, TEST_PL_NAME)
#         result = runner.invoke(app, ["search", TEST_PL_NAME])

#         # Clean up
#         pl_id = get_pl_id(sp, TEST_PL_NAME)
#         delete_playlist(sp, pl_id)

#         assert result.exit_code == 0
#         assert f"Found playlist {TEST_PL_NAME}" in result.stdout


#     def test_search_name_provided_and_playlist_DNE(self):
#         result = runner.invoke(app, ["search", TEST_PL_NAME])
#         assert result.exit_code == 1
#         assert f"Could not find {TEST_PL_NAME} in user's playlists." in result.stdout
