import re

from typer.testing import CliRunner
from app_strings import General, Create, Search, Unfollow, Follow
from dummy_spotipy import DummySpotipy
from spotipy_facade import USE_DUMMY_WRAPPER
from spotify_cli import spot, app

runner = CliRunner()

TEST_PL_NAME = "TEST_PL_NAME"


class TestCreate:
    def test_create_playlist(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        pl_exists = spot.check_exists(pl_id)
        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert pl_exists
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout

    def test_create_name_clash_no_force(self):
        spot.create_playlist(TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME])

        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert result.exit_code == 0
        assert Create.dupe_exist_no_f in result.stdout

    def test_create_name_clash_force(self):
        spot.create_playlist(TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--force"])

        pl_ids = spot.get_pl_id(TEST_PL_NAME)
        pl_exists = True
        for cur_id in pl_ids:
            pl_exists = spot.check_exists(cur_id)

        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert pl_exists
        assert result.exit_code == 0
        assert Create.dupe_created in result.stdout

    def test_create_with_description(self):
        desc = "A test playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--desc", desc])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        pl_exists = spot.check_exists(pl_id)
        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert pl_exists
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.desc_status.format(desc) in result.stdout

    def test_create_public(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--public"])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        pl_exists = spot.check_exists(pl_id)
        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert pl_exists
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.pub_status.format("True") in result.stdout

    def test_create_collaborative(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--collab"])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        pl_exists = spot.check_exists(pl_id)
        # Clean up
        spot.unfollow_playlist(pl_id)

        assert pl_exists
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.collab_status.format("True") in result.stdout


class TestFollow:
    def test_follow_pl_by_id(self):
        item_type = "playlist"
        test_name = "Massive Drum & Bass"
        pl_id = "37i9dQZF1DX5wDmLW735Yd"

        was_following = spot.following_playlist(pl_id)
        if was_following:
            spot.unfollow_playlist(pl_id)

        if USE_DUMMY_WRAPPER:
            spot.sp.create_non_followed_playlist(test_name, pl_id)
        result = runner.invoke(app, ["follow", item_type, pl_id])

        following = spot.following_playlist(pl_id)

        # Cleanup
        if following and not was_following:
            spot.unfollow_playlist(pl_id)

        assert following == True
        assert (
            Follow.followed.format(item_type, test_name, pl_id) in result.stdout
        )

    def test_follow_artist_by_id(self):
        test_name = "Weezer"
        item_type = "artist"
        artist_id = "3jOstUTkEu2JkjvRdBA5Gu"

        was_following = spot.sp.current_user_following_artists([artist_id])[0]
        if was_following:
            spot.sp.user_unfollow_artists([artist_id])

        if USE_DUMMY_WRAPPER:
            spot.sp.create_non_followed_artist(artist_id, test_name)
        result = runner.invoke(app, ["follow", item_type, artist_id])

        following = spot.sp.current_user_following_artists([artist_id])[0]

        # Cleanup
        if following and not was_following:
            spot.sp.user_unfollow_artists([artist_id])

        assert following == True
        assert (
            Follow.followed.format(item_type, test_name, artist_id)
            in result.stdout
        )


class TestUnfollow:
    def test_unfollow_artist_by_name(self):
        test_name = "Weezer"
        item_type = "artist"
        artist_id = "3jOstUTkEu2JkjvRdBA5Gu"
        if USE_DUMMY_WRAPPER:
            spot.sp.create_non_followed_artist(artist_id, test_name)
        spot.follow_artist(artist_id)
        result = runner.invoke(
            app, ["unfollow", item_type, test_name, "--no-prompt"]
        )

        following = spot.sp.current_user_following_artists([artist_id])[0]

        assert result.exit_code == 0
        assert not following
        assert (
            Unfollow.unfollowed_item.format(test_name, artist_id)
            in result.stdout
        )

    def test_unfollow_artist_by_id(self):
        test_name = "Weezer"
        item_type = "artist"
        artist_id = "3jOstUTkEu2JkjvRdBA5Gu"
        if USE_DUMMY_WRAPPER:
            spot.sp.create_non_followed_artist(artist_id, test_name)
        spot.follow_artist(artist_id)
        result = runner.invoke(
            app, ["unfollow", item_type, "--id", artist_id, "--no-prompt"]
        )

        following = spot.sp.current_user_following_artists([artist_id])[0]

        assert result.exit_code == 0
        assert not following
        assert (
            Unfollow.unfollowed_item.format(test_name, artist_id)
            in result.stdout
        )

    def test_unfollow_no_name_or_id(self):
        result = runner.invoke(app, ["unfollow", "playlist", "--no-prompt"])
        assert result.exit_code == 1
        assert General.spec_name_id in result.stdout

    def test_unfollow_pl_prompt_cancled(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        result = runner.invoke(
            app, ["unfollow", "playlist", TEST_PL_NAME], input="n\n"
        )

        # Cleanup
        spot.unfollow_playlist(pl_id)
        assert result.exit_code == 0
        assert General.op_canceled in result.stdout

    def test_unfollow_pl_prompt_approved(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)

        result = runner.invoke(
            app, ["unfollow", "playlist", TEST_PL_NAME], input="y\n"
        )
        pl_exists = spot.check_exists(pl_id)

        # Cleanup, if needed
        if pl_exists:
            spot.unfollow_playlist(pl_id)

        assert result.exit_code == 0
        assert (
            Unfollow.unfollowed_item.format(TEST_PL_NAME, pl_id)
            in result.stdout
        )
        assert not pl_exists

    def test_unfollow_pl_by_id(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)

        result = runner.invoke(
            app, ["unfollow", "playlist", "--id", pl_id], input="y\n"
        )
        pl_exists = spot.check_exists(pl_id)

        # Cleanup, if needed
        if pl_exists:
            spot.unfollow_playlist(pl_id)

        assert result.exit_code == 0
        assert (
            Unfollow.unfollowed_item.format(TEST_PL_NAME, pl_id)
            in result.stdout
        )
        assert not pl_exists

    def test_unfollow_pl_no_prompt(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)

        result = runner.invoke(
            app, ["unfollow", "playlist", "--no-prompt", TEST_PL_NAME]
        )
        pl_exists = spot.check_exists(pl_id)

        # Cleanup, if needed
        if pl_exists:
            spot.unfollow_playlist(pl_id)

        assert result.exit_code == 0
        assert (
            Unfollow.unfollowed_item.format(TEST_PL_NAME, pl_id)
            in result.stdout
        )
        assert not pl_exists

    def test_unfollow_pl_DNE(self):
        item_type = "playlist"
        result = runner.invoke(
            app, ["unfollow", item_type, TEST_PL_NAME], input="y\n"
        )
        assert result.exit_code == 1
        assert (
            General.item_DNE.format(item_type, "name", TEST_PL_NAME)
            in result.stdout
        )

    def test_unfollow_pl_name_clash_no_prompt(self):
        """
        Test deleting when multiple lists exist with same name and
        --no-prompt flag was used ()
        If multiple lists exist with given name, cli does not know
        which to unfollow. It should exit with code 1, and tell user.
        """
        pl_id1 = spot.create_playlist(TEST_PL_NAME)
        pl_id2 = spot.create_playlist(TEST_PL_NAME)

        result = runner.invoke(
            app, ["unfollow", "playlist", "--no-prompt", TEST_PL_NAME]
        )

        # Cleanup
        spot.unfollow_playlist(pl_id1)
        spot.unfollow_playlist(pl_id2)

        assert result.exit_code == 0
        assert Unfollow.dupes_found.format(TEST_PL_NAME) in result.stdout


class TestSearch:
    def test_search_no_name_provided(self):
        result = runner.invoke(app, ["search", "--user"])
        assert result.exit_code == 0
        assert Search.list_all in result.stdout

    def test_search_name_provided_and_playlist_exists(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        result = runner.invoke(app, ["search", TEST_PL_NAME])

        # Clean up
        spot.unfollow_playlist(pl_id)

        assert result.exit_code == 0
        assert Search.num_items_found.format(1, TEST_PL_NAME) in result.stdout

    def test_search_name_provided_and_playlist_DNE(self):
        result = runner.invoke(app, ["search", "--user", TEST_PL_NAME])
        assert result.exit_code == 1
        assert General.not_found.format(TEST_PL_NAME) in result.stdout

    def test_search_multiple_exist(self):
        pl_id1 = spot.create_playlist(TEST_PL_NAME)
        pl_id2 = spot.create_playlist(TEST_PL_NAME)
        result = runner.invoke(app, ["search", TEST_PL_NAME, "--user"])

        # Clean up
        spot.unfollow_playlist(pl_id1)
        spot.unfollow_playlist(pl_id2)

        assert result.exit_code == 0
        assert Search.num_items_found.format(2, TEST_PL_NAME) in result.stdout

    def test_search_public(self):
        if USE_DUMMY_WRAPPER:
            spot.create_playlist("Massive Drum & Bass")
        result = runner.invoke(app, ["search", "Massive Drum & Bass"])

        assert result.exit_code == 0
        assert Search.search_pub in result.stdout
        pattern = Search.num_items_found.replace("{}", r"\d+", 1)
        pattern = pattern.replace("{}", ".+", 1)
        assert re.search(pattern, result.stdout)

    def test_search_public_limit_results(self):
        if USE_DUMMY_WRAPPER:
            spot.create_playlist("Massive Drum & Bass")
        result = runner.invoke(
            app, ["search", "Massive Drum & Bass", "--limit", 5]
        )

        assert result.exit_code == 0
        assert Search.search_pub in result.stdout
        pattern = Search.num_items_found.replace("{}", r"\d+", 1)
        pattern = pattern.replace("{}", ".+", 1)
        assert re.search(pattern, result.stdout)

    def test_search_public_change_market(self):
        if USE_DUMMY_WRAPPER:
            spot.create_playlist("Massive Drum & Bass")
        result = runner.invoke(
            app, ["search", "Massive Drum & Bass", "--market", "GB"]
        )

        assert result.exit_code == 0
        assert Search.search_pub in result.stdout
        pattern = Search.num_items_found.replace("{}", r"\d+", 1)
        pattern = pattern.replace("{}", ".+", 1)
        assert re.search(pattern, result.stdout)


# Dumb hack for debugging test cases:
if __name__ == "__main__":
    # Run test case directly here

    # TestFollow().test_follow_pl_by_id()
    # TestFollow().test_follow_artist_by_id()
    # TestUnfollow().test_unfollow_artist_by_name()
    TestUnfollow().test_unfollow_artist_by_name()
    TestUnfollow().test_unfollow_artist_by_id()
