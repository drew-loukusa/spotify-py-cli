from os import name
import re
from typing import List, Literal

from typer.testing import CliRunner

from spotipy_facade import USE_DUMMY_WRAPPER
from spotify_cli import spot, app

from interfaces import Item, ItemCollection
from items import Show, Episode, Track, Playlist, Artist, Album
from user_libary import (
    FollowedPlaylists,
    FollowedArtists,
    SavedAlbums,
    SavedEpisodes,
    SavedShows,
    SavedTracks,
)
from app_strings import (
    General,
    Create,
    Listing,
    Search,
    Unfollow,
    Follow,
    Save,
    Unsave,
)

runner = CliRunner()

TEST_PL_NAME = "TEST_PL_NAME"


class TestCreate:
    def test_create_playlist(self):
        item_type = "playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        playlist = Playlist(spot.sp, pl_id)
        fp = FollowedPlaylists(spot.sp)
        following = fp.contains(playlist)
        # Clean up
        fp.remove(playlist)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout

    def test_create_name_clash_no_force(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        fp = FollowedPlaylists(spot.sp)
        result = runner.invoke(app, ["create", TEST_PL_NAME])

        # Clean up
        fp.remove(Playlist(spot.sp, pl_id))

        assert result.exit_code == 0
        assert Create.dupe_exist_no_f in result.stdout

    def test_create_name_clash_force(self):
        item_type = "playlist"
        spot.create_playlist(TEST_PL_NAME)
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--force"])

        pl_ids = spot.get_pl_id(TEST_PL_NAME)
        following = True
        for cur_id in pl_ids:
            following = FollowedPlaylists(spot.sp).contains(
                Playlist(spot.sp, cur_id)
            )

        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.dupe_created in result.stdout

    def test_create_with_description(self):
        desc = "A test playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--desc", desc])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        following = FollowedPlaylists(spot.sp).contains(
            Playlist(spot.sp, pl_id)
        )
        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.desc_status.format(desc) in result.stdout

    def test_create_public(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--public"])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        following = FollowedPlaylists(spot.sp).contains(
            Playlist(spot.sp, pl_id)
        )
        # Clean up
        spot.unfollow_all_pl(TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.pub_status.format("True") in result.stdout

    def test_create_collaborative(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--collab"])
        pl_id = spot.get_pl_id(TEST_PL_NAME)[0]
        playlist = Playlist(spot.sp, pl_id)
        fp = FollowedPlaylists(spot.sp)
        following = fp.contains(playlist)
        # Clean up
        fp.remove(playlist)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.collab_status.format("True") in result.stdout


# Configurable function for other tests to use
# End with _ so pytest doesnt't run this
def modify_collection_test_(
    action: str,
    item_name: str,
    item_type: str,
    item_id: str,
    ItemClass: Item,
    Collection: ItemCollection,
    output_text: str,
    flags: List[str] = None,
):
    """
    action:     'follow' | 'unfollow' | 'save' | 'unsave'
    item_type:  'playlist' | 'artist' | 'album' | 'track' | 'show' | 'episode'
    ItemClass:  Playlist | Artist | Album | Track | Show | Episode
    Collection: FollowedPlaylists | FollowedArtists | SavedAlbums | SavedTracks | SavedShows | SavedEpisodes
    output_text: What text should appear in standard out as result of command run
    flags: Additional flags to be used with the commmand
    """
    item = ItemClass(spot.sp, item_id)
    collection = Collection(spot.sp)

    was_contained = collection.contains(item)
    if was_contained and action in {"follow", "save"}:
        collection.remove(item)

    if USE_DUMMY_WRAPPER:
        extern = False
        if action in {"follow", "save"}:
            extern = True
        spot.sp.create_item(
            item_type=item_type,
            item_id=item_id,
            item_name=item_name,
            extern=extern,
        )
    args = [action, item_type, item_id]
    if flags is not None:
        args.extend(flags)
    result = runner.invoke(app, args=args)
    contained = collection.contains(item)

    if action in {"follow", "save"}:
        # Cleanup
        if contained and not was_contained:
            collection.remove(item)
        assert contained == True

    elif action in {"unfollow", "unsave"}:
        # Cleanup
        if not contained and was_contained:
            collection.add(item)
        assert contained == False

    assert output_text in result.stdout


class TestFollow:
    def test_follow_pl_by_id(self):
        item_type = "playlist"
        item_name = "Massive Drum & Bass"
        item_id = "37i9dQZF1DX5wDmLW735Yd"

        modify_collection_test_(
            action="follow",
            item_name=item_name,
            item_type="playlist",
            item_id=item_id,
            ItemClass=Playlist,
            Collection=FollowedPlaylists,
            output_text=Follow.followed.format(item_type, item_name, item_id),
        )

    def test_follow_artist_by_id(self):
        item_name = "Weezer"
        item_type = "artist"
        item_id = "3jOstUTkEu2JkjvRdBA5Gu"
        output_text = Follow.followed.format(item_type, item_name, item_id)

        modify_collection_test_(
            action="follow",
            item_name=item_name,
            item_type=item_type,
            item_id=item_id,
            ItemClass=Artist,
            Collection=FollowedArtists,
            output_text=output_text,
        )


class TestSave:
    def _test_save_item(
        self,
        item_name: str,
        item_type: str,
        item_id: str,
        ItemClass: Item,
        Collection: ItemCollection,
    ):
        output_text = Save.saved.format(item_type, item_name, item_id)
        modify_collection_test_(
            action="save",
            item_name=item_name,
            item_type=item_type,
            item_id=item_id,
            ItemClass=ItemClass,
            Collection=Collection,
            output_text=output_text,
        )

    def test_save_episode(self):
        item_name = "003: I Need a Moment!"
        item_type = "episode"
        item_id = "0UGR0O3f4qiVq2npDPWTvk"
        self._test_save_item(
            item_name=item_name,
            item_type=item_type,
            item_id=item_id,
            ItemClass=Episode,
            Collection=SavedEpisodes,
        )

    def test_save_track(self):
        self._test_save_item(
            item_name="Behind The Glass",
            item_type="track",
            item_id="3Dd0R86fWYsKSk70EhBZ8v",
            ItemClass=Track,
            Collection=SavedTracks,
        )

    def test_save_show(self):
        self._test_save_item(
            item_name="Giant Bombcast",
            item_type="show",
            item_id="5as3aKmN2k11yfDDDSrvaZ",
            ItemClass=Show,
            Collection=SavedShows,
        )

    def test_save_album(self):
        self._test_save_item(
            item_name="Portals",
            item_type="album",
            item_id="6SC0Omssa5QQtX22zlZGEG",
            ItemClass=Album,
            Collection=SavedAlbums,
        )


class TestUnfollow:
    def unfollow_item(
        self,
        item_name: str,
        item_type: str,
        item_id: str,
        ItemClass: Item,
        Collection: ItemCollection,
        flags: List[str],
    ):
        output_text = Unfollow.unfollowed_item.format(item_name, item_id)
        modify_collection_test_(
            action="unfollow",
            item_name=item_name,
            item_type=item_type,
            item_id=item_id,
            ItemClass=ItemClass,
            Collection=Collection,
            output_text=output_text,
            flags=flags,
        )

    def test_unfollow_artist_by_id(self):
        self.unfollow_item(
            item_name="Weezer",
            item_type="artist",
            item_id="3jOstUTkEu2JkjvRdBA5Gu",
            ItemClass=Artist,
            Collection=FollowedArtists,
            flags=["--no-prompt"],
        )

    def test_unfollow_pl_prompt_cancled(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        playlist = Playlist(spot.sp, pl_id)
        result = runner.invoke(
            app, ["unfollow", "playlist", pl_id], input="n\n"
        )
        # Cleanup
        fp = FollowedPlaylists(spot.sp)
        fp.remove(playlist)

        assert result.exit_code == 0
        assert General.op_canceled in result.stdout

    def test_unfollow_pl_prompt_approved(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        playlist = Playlist(spot.sp, pl_id)
        fp = FollowedPlaylists(spot.sp)

        result = runner.invoke(
            app, ["unfollow", "playlist", pl_id], input="y\n"
        )
        following = fp.contains(playlist)

        # Cleanup, if needed
        if following:
            fp.remove(playlist)

        assert not following
        assert result.exit_code == 0
        assert (
            Unfollow.unfollowed_item.format(TEST_PL_NAME, pl_id)
            in result.stdout
        )

    def test_unfollow_pl_no_prompt(self):
        self.unfollow_item(
            item_type="playlist",
            item_name="Massive Drum & Bass",
            item_id="37i9dQZF1DX5wDmLW735Yd",
            ItemClass=Playlist,
            Collection=FollowedPlaylists,
            flags=["--no-prompt"],
        )

    def test_unfollow_pl_DNE(self):
        item_type = "playlist"
        result = runner.invoke(
            app, ["unfollow", item_type, "DNE_ID"], input="y\n"
        )
        assert result.exit_code == 1
        assert (
            General.item_DNE.format(item_type, "id", "DNE_ID") in result.stdout
        )


class TestUnsave:
    def unsave_item(
        self,
        item_name: str,
        item_type: str,
        item_id: str,
        ItemClass: Item,
        Collection: ItemCollection,
    ):
        output_text = Unsave.unsaved.format(item_type, item_name, item_id)
        modify_collection_test_(
            action="unsave",
            item_name=item_name,
            item_type=item_type,
            item_id=item_id,
            ItemClass=ItemClass,
            Collection=Collection,
            output_text=output_text,
        )

    def test_unsave_episode(self):
        self.unsave_item(
            item_name="003: I Need a Moment!",
            item_type="episode",
            item_id="0UGR0O3f4qiVq2npDPWTvk",
            ItemClass=Episode,
            Collection=SavedEpisodes,
        )

    def test_unsave_track(self):
        self.unsave_item(
            item_name="Behind The Glass",
            item_type="track",
            item_id="3Dd0R86fWYsKSk70EhBZ8v",
            ItemClass=Track,
            Collection=SavedTracks,
        )

    def test_unsave_show(self):
        self.unsave_item(
            item_name="Giant Bombcast",
            item_type="show",
            item_id="5as3aKmN2k11yfDDDSrvaZ",
            ItemClass=Show,
            Collection=SavedShows,
        )

    def test_unsave_album(self):
        self.unsave_item(
            item_name="Portals",
            item_type="album",
            item_id="6SC0Omssa5QQtX22zlZGEG",
            ItemClass=Album,
            Collection=SavedAlbums,
        )


class TestSearch:
    def test_search_no_name_provided(self):
        result = runner.invoke(app, ["search", "playlist", "--user"])
        assert result.exit_code == 0
        assert Search.list_all in result.stdout

    def test_search_name_provided_and_playlist_exists(self):
        pl_id = spot.create_playlist(TEST_PL_NAME)
        playlist = Playlist(spot.sp, pl_id)
        fp = FollowedPlaylists(spot.sp)
        result = runner.invoke(app, ["search", "playlist", TEST_PL_NAME])

        # Clean up
        fp.remove(playlist)

        assert result.exit_code == 0
        assert (
            Search.num_items_found.format("", TEST_PL_NAME).replace(
                "Found ", ""
            )
            in result.stdout
        )

    def test_search_name_provided_and_playlist_DNE(self):
        result = runner.invoke(
            app, ["search", "playlist", "--user", TEST_PL_NAME]
        )
        assert result.exit_code == 1
        assert General.not_found.format(TEST_PL_NAME) in result.stdout

    def test_search_multiple_exist(self):
        pl_id1 = spot.create_playlist(TEST_PL_NAME)
        pl_id2 = spot.create_playlist(TEST_PL_NAME)
        play1 = Playlist(spot.sp, pl_id1)
        play2 = Playlist(spot.sp, pl_id2)
        result = runner.invoke(
            app, ["search", "playlist", TEST_PL_NAME, "--user"]
        )

        fp = FollowedPlaylists(spot.sp)
        # Clean up
        fp.remove(play1)
        fp.remove(play2)

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


class TestList:
    def _test_list(self, *args):
        item_type = args[0]
        output_text = Listing.listing
        args = ["list"] + list(args)
        result = runner.invoke(app, args)
        assert output_text.format(item_type) in result.stdout

        if "--retrieve-all" not in args:
            limit, offset, = (
                10,
                0,
            )
            for i, arg in enumerate(args):
                if arg == "--limit":
                    limit = args[i + 1]
                if arg == "--offset":
                    offset = args[i + 1]
            assert Listing.params.format(limit, offset) in result.stdout
        else:
            assert Listing.ret_all in result.stdout
        assert result.exit_code == 0

    def test_list_followed_playlists(self):
        self._test_list("playlist")

    def test_list_followed_artists(self):
        self._test_list("artist")

    def test_list_followed_albums(self):
        self._test_list("album")

    def test_list_followed_shows(self):
        self._test_list("show")

    def test_list_followed_tracks(self):
        self._test_list("track")

    def test_list_followed_episodes(self):
        self._test_list("episode")

    def test_limit_change(self):
        self._test_list("track", "--limit", 100)

    def test_limit_change(self):
        self._test_list("track", "--offset", 50)

    def test_retrieve_all(self):
        self._test_list("track", "--retrieve-all")


# NOTE: Tests involving name are commented out because I've stripped out
#       being able to use NAME to specify what items to unfollow... For now.
#       I'm trying switch to using interfaces to do things, and the added complexity from
#       trying to support selection by name is getting in my way.
#       These tests will come back at a later date, probably.

# Most of these go into "Unfollow"
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

# def test_unfollow_artist_by_name(self):
#     item_name = "Weezer"
#     item_type = "artist"
#     item_id = "3jOstUTkEu2JkjvRdBA5Gu"
#     if USE_DUMMY_WRAPPER:
#         spot.sp.create_non_followed_artist(item_id, item_name)
#     spot.get_followable(item_type, item_id).follow()
#     #spot.follow_artist(item_id)
#     result = runner.invoke(
#         app, ["unfollow", item_type, item_name, "--no-prompt"]
#     )

#     following = spot.sp.current_user_following_artists([item_id])[0]

#     assert result.exit_code == 0
#     assert not following
#     assert (
#         Unfollow.unfollowed_item.format(item_name, item_id)
#         in result.stdout
#     )

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

# def test_unfollow_no_name_or_id(self):
#     result = runner.invoke(app, ["unfollow", "playlist", "--no-prompt"])
#     assert result.exit_code == 1
#     assert General.spec_name_id in result.stdout
