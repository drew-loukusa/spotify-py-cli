import re

from typer.testing import CliRunner
from app_strings import General, Create, Search, Unfollow, Follow
from spotipy_facade import USE_DUMMY_WRAPPER
from spotify_cli import spot, app
from concrete import Playlist, Artist

runner = CliRunner()

TEST_PL_NAME = "TEST_PL_NAME"


class TestCreate:
    def test_create_playlist(self):
        item_type = "playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        playlist: Playlist = spot.get_item(item_type, pl_id)
        following = playlist.following()
        # Clean up
        playlist.unfollow()

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout

    def test_create_name_clash_no_force(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        playlist: Playlist = spot.get_item("playlist", pl_id)
        result = runner.invoke(app, ["create", TEST_PL_NAME])

        # Clean up
        playlist.unfollow()

        assert result.exit_code == 0
        assert Create.dupe_exist_no_f in result.stdout

    def test_create_name_clash_force(self):
        item_type = "playlist"
        spot.create_playlist(TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--force"])

        pl_ids = spot.get_pl_id(TEST_PL_NAME)
        following = True
        for cur_id in pl_ids:
            following = spot.get_item(item_type, cur_id).following()

        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.dupe_created in result.stdout

    def test_create_with_description(self):
        desc = "A test playlist"
        item_type = "playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--desc", desc])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        following = spot.get_item(item_type, pl_id).following()
        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.desc_status.format(desc) in result.stdout

    def test_create_public(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--public"])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        item_type = "playlist"
        following = spot.get_item(item_type, pl_id).following()
        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.pub_status.format("True") in result.stdout

    def test_create_collaborative(self):
        item_type = "playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--collab"])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        playlist: Playlist = spot.get_item(item_type, pl_id)
        following = playlist.following()
        # Clean up
        playlist.unfollow()

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.collab_status.format("True") in result.stdout


class TestFollow:
    def test_follow_pl_by_id(self):
        item_type = "playlist"
        test_name = "Massive Drum & Bass"
        pl_id = "37i9dQZF1DX5wDmLW735Yd"

        playlist: Playlist = spot.get_item(item_type, pl_id)
        was_following = playlist.following()
        if was_following:
            playlist.unfollow()

        if USE_DUMMY_WRAPPER:
            spot.sp.create_non_followed_playlist(test_name, pl_id)
        result = runner.invoke(app, ["follow", item_type, pl_id])

        following = playlist.following()

        # Cleanup
        if following and not was_following:
            playlist.unfollow()

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

        following = spot.get_item(item_type, artist_id).following()

        # Cleanup
        if following and not was_following:
            spot.sp.user_unfollow_artists([artist_id])

        assert following == True
        assert (
            Follow.followed.format(item_type, test_name, artist_id)
            in result.stdout
        )


class TestUnfollow:

    # NOTE: Tests involving name are commented out because I've stripped out
    #       being able to use NAME to specify what items to unfollow... For now.
    #       I'm trying switch to using interfaces to do things, and the added complexity from
    #       trying to support selection by name is getting in my way.
    #       These tests will come back at a later date, probably.

    # def test_unfollow_artist_by_name(self):
    #     test_name = "Weezer"
    #     item_type = "artist"
    #     artist_id = "3jOstUTkEu2JkjvRdBA5Gu"
    #     if USE_DUMMY_WRAPPER:
    #         spot.sp.create_non_followed_artist(artist_id, test_name)
    #     spot.get_followable(item_type, artist_id).follow()
    #     #spot.follow_artist(artist_id)
    #     result = runner.invoke(
    #         app, ["unfollow", item_type, test_name, "--no-prompt"]
    #     )

    #     following = spot.sp.current_user_following_artists([artist_id])[0]

    #     assert result.exit_code == 0
    #     assert not following
    #     assert (
    #         Unfollow.unfollowed_item.format(test_name, artist_id)
    #         in result.stdout
    #     )

    def test_unfollow_artist_by_id(self):
        test_name = "Weezer"
        item_type = "artist"
        artist_id = "3jOstUTkEu2JkjvRdBA5Gu"
        if USE_DUMMY_WRAPPER:
            spot.sp.create_non_followed_artist(artist_id, test_name)
        artist: Artist = spot.get_item(item_type, artist_id)
        artist.follow()
        result = runner.invoke(
            app, ["unfollow", item_type, artist_id, "--no-prompt"]
        )

        following = artist.following()

        if following:
            artist.unfollow()

        assert result.exit_code == 0
        assert not following
        assert (
            Unfollow.unfollowed_item.format(test_name, artist_id)
            in result.stdout
        )

    # def test_unfollow_no_name_or_id(self):
    #     result = runner.invoke(app, ["unfollow", "playlist", "--no-prompt"])
    #     assert result.exit_code == 1
    #     assert General.spec_name_id in result.stdout

    def test_unfollow_pl_prompt_cancled(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        playlist: Playlist = spot.get_item("playlist", pl_id)
        result = runner.invoke(
            app, ["unfollow", "playlist", pl_id], input="n\n"
        )

        # Cleanup
        playlist.unfollow()
        assert result.exit_code == 0
        assert General.op_canceled in result.stdout

    def test_unfollow_pl_prompt_approved(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        playlist: Playlist = spot.get_item("playlist", pl_id)

        result = runner.invoke(
            app, ["unfollow", "playlist", pl_id], input="y\n"
        )
        following = playlist.following()

        # Cleanup, if needed
        if following:
            playlist.unfollow()

        assert result.exit_code == 0
        assert (
            Unfollow.unfollowed_item.format(TEST_PL_NAME, pl_id)
            in result.stdout
        )
        assert not following

    # Redundant for now, since ID is the only thing supported
    # def test_unfollow_pl_by_id(self):
    #     pl_id = spot.create_playlist(TEST_PL_NAME)

    #     result = runner.invoke(
    #         app, ["unfollow", "playlist", "--id", pl_id], input="y\n"
    #     )
    #     item_type = "playlist"
    #     following = spot.get_item(item_type, pl_id).following()

    #     # Cleanup, if needed
    #     if following:
    #         spot.unfollow_playlist(pl_id)

    #     assert result.exit_code == 0
    #     assert (
    #         Unfollow.unfollowed_item.format(TEST_PL_NAME, pl_id)
    #         in result.stdout
    #     )
    #     assert not following

    def test_unfollow_pl_no_prompt(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        playlist: Playlist = spot.get_item("playlist", pl_id)
        result = runner.invoke(
            app, ["unfollow", "playlist", "--no-prompt", pl_id]
        )
        following = playlist.following()

        # Cleanup, if needed
        if following:
            playlist.unfollow()

        assert result.exit_code == 0
        assert (
            Unfollow.unfollowed_item.format(TEST_PL_NAME, pl_id)
            in result.stdout
        )
        assert not following

    def test_unfollow_pl_DNE(self):
        item_type = "playlist"
        result = runner.invoke(
            app, ["unfollow", item_type, "DNE_ID"], input="y\n"
        )
        assert result.exit_code == 1
        assert (
            General.item_DNE.format(item_type, "id", "DNE_ID") in result.stdout
        )

    # def test_unfollow_pl_name_clash_no_prompt(self):
    #     """
    #     Test deleting when multiple lists exist with same name and
    #     --no-prompt flag was used ()
    #     If multiple lists exist with given name, cli does not know
    #     which to unfollow. It should exit with code 1, and tell user.
    #     """
    #     pl_id1 = spot.create_playlist(TEST_PL_NAME)
    #     pl_id2 = spot.create_playlist(TEST_PL_NAME)

    #     result = runner.invoke(
    #         app, ["unfollow", "playlist", "--no-prompt", TEST_PL_NAME]
    #     )

    #     # Cleanup
    #     spot.unfollow_playlist(pl_id1)
    #     spot.unfollow_playlist(pl_id2)

    #     assert result.exit_code == 0
    #     assert Unfollow.dupes_found.format(TEST_PL_NAME) in result.stdout


class TestSearch:
    def test_search_no_name_provided(self):
        result = runner.invoke(app, ["search", "playlist", "--user"])
        assert result.exit_code == 0
        assert Search.list_all in result.stdout

    def test_search_name_provided_and_playlist_exists(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        playlist: Playlist = spot.get_item("playlist", pl_id)
        result = runner.invoke(app, ["search", "playlist", TEST_PL_NAME])

        # Clean up
        playlist.unfollow()

        assert result.exit_code == 0
        assert Search.num_items_found.format(1, TEST_PL_NAME) in result.stdout

    def test_search_name_provided_and_playlist_DNE(self):
        result = runner.invoke(
            app, ["search", "playlist", "--user", TEST_PL_NAME]
        )
        assert result.exit_code == 1
        assert General.not_found.format(TEST_PL_NAME) in result.stdout

    def test_search_multiple_exist(self):
        pl_id1 = spot.create_playlist(TEST_PL_NAME)
        play1: Playlist = spot.get_item("playlist", pl_id1)
        pl_id2 = spot.create_playlist(TEST_PL_NAME)
        play2: Playlist = spot.get_item("playlist", pl_id2)
        result = runner.invoke(
            app, ["search", "playlist", TEST_PL_NAME, "--user"]
        )

        # Clean up
        play1.unfollow()
        play2.unfollow()

        assert result.exit_code == 0
        assert Search.num_items_found.format(2, TEST_PL_NAME) in result.stdout

    def test_search_public(self):
        if USE_DUMMY_WRAPPER:
            spot.create_playlist("Massive Drum & Bass")
        result = runner.invoke(
            app, ["search", "playlist", "Massive Drum & Bass"]
        )

        assert result.exit_code == 0
        assert Search.search_pub in result.stdout
        pattern = Search.num_items_found.replace("{}", r"\d+", 1)
        pattern = pattern.replace("{}", ".+", 1)
        assert re.search(pattern, result.stdout)

    def test_search_public_limit_results(self):
        if USE_DUMMY_WRAPPER:
            spot.create_playlist("Massive Drum & Bass")
        result = runner.invoke(
            app, ["search", "playlist", "Massive Drum & Bass", "--limit", 5]
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
            app, ["search", "playlist", "Massive Drum & Bass", "--market", "GB"]
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
    # TestUnfollow().test_unfollow_artist_by_name()
    TestUnfollow().test_unfollow_artist_by_id()
    # TestSearch().test_search_multiple_exist()
    # TestSearch().test_search_name_provided_and_playlist_exists()
    pass
