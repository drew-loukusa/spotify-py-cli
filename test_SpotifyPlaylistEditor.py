import re
from os import name
from time import sleep

from AppStrings import *
from SpotifyUtils import *
from typer.testing import CliRunner
from SpotifyPlaylistEditor import USE_DUMMY_WRAPPER, sp, app

runner = CliRunner()

TEST_PL_NAME = "TEST_PL_NAME"


class TestCreate:
    def test_create_playlist(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME])
        pl_id = get_pl_id(sp, TEST_PL_NAME)[0]
        pl_exists = check_exists(sp, pl_id)
        # Clean up
        delete_all(sp, TEST_PL_NAME)

        assert pl_exists == True
        assert result.exit_code == 0
        assert Create.playlist_created in result.stdout

    def test_create_name_clash_no_force(self):
        create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME])

        # Clean up
        delete_all(sp, TEST_PL_NAME)

        assert result.exit_code == 0
        assert Create.dupe_exists_no_force in result.stdout

    def test_create_name_clash_force(self):
        create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--force"])

        pl_ids = get_pl_id(sp, TEST_PL_NAME)
        pl_exists = True
        for id in pl_ids:
            pl_exists = check_exists(sp, id)

        # Clean up
        delete_all(sp, TEST_PL_NAME)

        assert pl_exists == True
        assert result.exit_code == 0
        assert Create.duplicate_created in result.stdout

    def test_create_with_description(self):
        desc = "A test playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--desc", desc])
        pl_id = get_pl_id(sp, TEST_PL_NAME)[0]
        pl_exists = check_exists(sp, pl_id)
        # Clean up
        delete_all(sp, TEST_PL_NAME)

        assert pl_exists == True
        assert result.exit_code == 0
        assert Create.playlist_created in result.stdout
        assert Create.desc_status.format(desc) in result.stdout

    def test_create_public(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--public"])
        pl_id = get_pl_id(sp, TEST_PL_NAME)[0]
        pl_exists = check_exists(sp, pl_id)
        # Clean up
        delete_all(sp, TEST_PL_NAME)

        assert pl_exists == True
        assert result.exit_code == 0
        assert Create.playlist_created in result.stdout
        assert Create.pub_status.format("True") in result.stdout

    def test_create_collaborative(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--collab"])
        pl_id = get_pl_id(sp, TEST_PL_NAME)[0]
        pl_exists = check_exists(sp, pl_id)
        # Clean up
        delete_playlist(sp, pl_id)

        assert pl_exists == True
        assert result.exit_code == 0
        assert Create.playlist_created in result.stdout
        assert Create.collab_status.format("True") in result.stdout


class TestDelete:
    def test_delete_no_name_or_id(self):
        result = runner.invoke(app, ["delete", "--no-prompt"])
        assert result.exit_code == 1
        assert Delete.specify_name_or_id in result.stdout

    def test_delete_prompt_cancled(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="n\n")

        # Cleanup
        delete_playlist(sp, pl_id)
        assert result.exit_code == 0
        assert General.operation_canceled in result.stdout

    def test_delete_prompt_approved(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\n")
        pl_exists = check_exists(sp, pl_id)

        # Cleanup, if needed
        if pl_exists:
            delete_playlist(sp, pl_id)

        assert result.exit_code == 0
        assert Delete.deleted_playlist.format(TEST_PL_NAME, pl_id) in result.stdout
        assert pl_exists == False

    def test_delete_by_id(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", "--id", pl_id], input="y\n")
        pl_exists = check_exists(sp, pl_id)

        # Cleanup, if needed
        if pl_exists:
            delete_playlist(sp, pl_id)

        assert result.exit_code == 0
        assert Delete.deleted_playlist.format(TEST_PL_NAME, pl_id) in result.stdout
        assert pl_exists == False

    def test_delete_no_prompt(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", "--no-prompt", TEST_PL_NAME])
        pl_exists = check_exists(sp, pl_id)

        # Cleanup, if needed
        if pl_exists:
            delete_playlist(sp, pl_id)

        assert result.exit_code == 0
        assert Delete.deleted_playlist.format(TEST_PL_NAME, pl_id) in result.stdout
        assert pl_exists == False

    def test_delete_playlist_DNE(self):
        result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\n")
        assert result.exit_code == 1
        assert (
            f"Playlist with name: '{TEST_PL_NAME}' appears to not exist!"
            in result.stdout
        )

    # Commented out tests for possible future behavior.
    # def test_delete_name_clash_prompt_select_single(self):
    #     """
    #     Test deleting when multiple playlists share the same name.
    #     Prompt user if they want to proceed.
    #     User selects one playlist to be deleted.
    #     """
    #     pl_id1 = create_playlist(sp, TEST_PL_NAME)
    #     pl_id2 = create_playlist(sp, TEST_PL_NAME)

    #     result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\n1\n")
    #     pl_exists = check_exists(sp, pl_id1)

    #     # Cleanup
    #     delete_playlist(sp, pl_id2)
    #     if pl_exists:
    #         delete_playlist(sp, pl_id1)

    #     assert result.exit_code == 0
    #     assert (
    #         f"Multiple playlists were found with name: {TEST_PL_NAME}" in result.stdout
    #     )
    #     assert pl_exists == False

    # def test_delete_name_clash_prompt_select_all(self):
    #     """
    #     Test deleting multiple playlists.
    #     Prompt user if they want to proceed.
    #     User selects all playlists to be deleted.
    #     """
    #     pl_id1 = create_playlist(sp, TEST_PL_NAME)
    #     pl_id2 = create_playlist(sp, TEST_PL_NAME)

    #     result = runner.invoke(app, ["delete", TEST_PL_NAME], input="y\nall\n")
    #     pl1_exists = check_exists(sp, pl_id1)
    #     pl2_exists = check_exists(sp, pl_id1)

    #     # Cleanup, if needed
    #     if pl1_exists:
    #         delete_playlist(sp, pl_id1)
    #     if pl2_exists:
    #         delete_playlist(sp, pl_id2)

    #     assert result.exit_code == 0
    #     assert (
    #         f"Multiple playlists were found with name: {TEST_PL_NAME}" in result.stdout
    #     )
    #     assert pl1_exists == False
    #     assert pl2_exists == False

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
        assert Delete.duplicates_found.format(TEST_PL_NAME) in result.stdout

    def test_delete_name_clash_prompt_all(self):
        """
        Test deleting when multiple lists exist with same name and
        --no-prompt flag was used ()
        If multiple lists exist with given name, cli does not know
        which to delete. It should exit with code 1, and tell user.
        """
        pl_id1 = create_playlist(sp, TEST_PL_NAME)
        pl_id2 = create_playlist(sp, TEST_PL_NAME)

        result = runner.invoke(app, ["delete", "--all", TEST_PL_NAME])

        # Cleanup
        delete_playlist(sp, pl_id1)
        delete_playlist(sp, pl_id2)

        assert result.exit_code == 0
        assert Delete.duplicates_found.format(TEST_PL_NAME) in result.stdout


class TestSearch:
    def test_search_no_name_provided(self):
        result = runner.invoke(app, ["search"])
        assert result.exit_code == 0
        assert Search.listing_all in result.stdout

    def test_search_name_provided_and_playlist_exists(self):
        pl_id = create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["search", TEST_PL_NAME])

        # Clean up
        delete_playlist(sp, pl_id)

        assert result.exit_code == 0
        assert General.num_playlists_found.format(1, TEST_PL_NAME) in result.stdout

    def test_search_name_provided_and_playlist_DNE(self):
        result = runner.invoke(app, ["search", TEST_PL_NAME])
        assert result.exit_code == 1
        assert General.not_found.format(TEST_PL_NAME) in result.stdout

    def test_search_multiple_exist(self):
        pl_id1 = create_playlist(sp, TEST_PL_NAME)
        pl_id2 = create_playlist(sp, TEST_PL_NAME)
        result = runner.invoke(app, ["search", TEST_PL_NAME])

        # Clean up
        delete_playlist(sp, pl_id1)
        delete_playlist(sp, pl_id2)

        assert result.exit_code == 0
        assert General.num_playlists_found.format(2, TEST_PL_NAME) in result.stdout

    def test_search_public(self):
        if USE_DUMMY_WRAPPER:
            create_playlist(sp, "Massive Drum & Bass")
        result = runner.invoke(app, ["search", "Massive Drum & Bass", "--public"])

        assert result.exit_code == 0
        assert Search.search_public in result.stdout
        pattern = Search.num_public.replace("{}", r"\d+", 1)
        pattern = pattern.replace("{}", ".+", 1)
        assert re.search(pattern, result.stdout)

    def test_search_public_limit_results(self):
        if USE_DUMMY_WRAPPER:
            create_playlist(sp, "Massive Drum & Bass")
        result = runner.invoke(
            app, ["search", "Massive Drum & Bass", "--public", "--limit", 5]
        )

        assert result.exit_code == 0
        assert Search.search_public in result.stdout
        pattern = Search.num_public.replace("{}", r"\d+", 1)
        pattern = pattern.replace("{}", ".+", 1)
        assert re.search(pattern, result.stdout)

    def test_search_public_change_market(self):
        if USE_DUMMY_WRAPPER:
            create_playlist(sp, "Massive Drum & Bass")
        result = runner.invoke(
            app, ["search", "Massive Drum & Bass", "--public", "--market", "GB"]
        )

        assert result.exit_code == 0
        assert Search.search_public in result.stdout
        pattern = Search.num_public.replace("{}", r"\d+", 1)
        pattern = pattern.replace("{}", ".+", 1)
        assert re.search(pattern, result.stdout)

    # TODO:
    # * Write test case for search flag '--market'
    # * Write test case for search flag '--limit'
    # * implement '--market' '--limit' for search
    # Move strings from editor to AppStrings, from the new search functionality


# Dumb hack for debugging test cases:

# Uncomment this:
# import os

# Put this at the top of SpotifyPlaylistEditor.py:
# os.environ['USE_DUMMY_WRAPPER'] = 'True'

# Run test case directly here.
TestSearch().test_search_public()
