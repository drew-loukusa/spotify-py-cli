import re
from typing import List

from typer.testing import CliRunner

from cli.facade.spotipy_facade import USE_DUMMY_WRAPPER
from cli.spotify_cli import spot, app

from cli.facade.interfaces import Item, ItemCollection
from cli.facade.items import Show, Episode, Track, Playlist, Artist, Album
from cli.facade.user_libary import (
    FollowedPlaylists,
    FollowedArtists,
    SavedAlbums,
    SavedEpisodes,
    SavedShows,
    SavedTracks,
)
from cli.app_strings import (
    Edit,
    General,
    Create,
    Listing,
    Search,
    Unfollow,
    Follow,
    Save,
    Unsave,
)
from . import testing_utils as tu

runner = CliRunner()

TEST_PL_NAME = "TEST_PL_NAME"


class TestCreate:
    def test_create_playlist(self):
        item_type = "playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME])
        pl_id = tu.get_pl_id(spot.sp, TEST_PL_NAME)[0]
        playlist = Playlist(spot.sp, pl_id)
        fp = FollowedPlaylists(spot.sp)
        following = fp.contains(playlist)
        # Clean up
        fp.remove(playlist)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout

    def test_create_name_clash_no_force(self):
        pl_id = spot.create_playlist(TEST_PL_NAME).id
        fp = FollowedPlaylists(spot.sp)
        result = runner.invoke(app, ["create", TEST_PL_NAME])

        # Clean up
        fp.remove(Playlist(spot.sp, pl_id))

        assert result.exit_code == 0
        assert Create.dupe_exist_no_f in result.stdout

    def test_create_name_clash_force(self):
        item_type = "playlist"
        spot.create_playlist(TEST_PL_NAME).id
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--force"])

        pl_ids = tu.get_pl_id(spot.sp, TEST_PL_NAME)
        following = True
        for cur_id in pl_ids:
            following = FollowedPlaylists(spot.sp).contains(
                Playlist(spot.sp, cur_id)
            )

        # Clean up
        tu.unfollow_all_pl(spot.sp, TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.dupe_created in result.stdout

    def test_create_with_description(self):
        desc = "A test playlist"
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--desc", desc])
        pl_id = tu.get_pl_id(spot.sp, TEST_PL_NAME)[0]
        following = FollowedPlaylists(spot.sp).contains(
            Playlist(spot.sp, pl_id)
        )
        # Clean up
        tu.unfollow_all_pl(spot.sp, TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.desc_status.format(desc) in result.stdout

    def test_create_public(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--public"])
        pl_id = tu.get_pl_id(spot.sp, TEST_PL_NAME)[0]
        following = FollowedPlaylists(spot.sp).contains(
            Playlist(spot.sp, pl_id)
        )
        # Clean up
        tu.unfollow_all_pl(spot.sp, TEST_PL_NAME)

        assert following
        assert result.exit_code == 0
        assert Create.plist_created in result.stdout
        assert Create.pub_status.format("True") in result.stdout

    def test_create_collaborative(self):
        result = runner.invoke(app, ["create", TEST_PL_NAME, "--collab"])
        pl_id = tu.get_pl_id(spot.sp, TEST_PL_NAME)[0]
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
        pl_id = spot.create_playlist(TEST_PL_NAME).id
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
        pl_id = spot.create_playlist(TEST_PL_NAME).id
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
        assert Unfollow.item_DNE.format("DNE_ID") in result.stdout


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
        pl_id = spot.create_playlist(TEST_PL_NAME).id
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
        play1 = spot.create_playlist(TEST_PL_NAME)
        play2 = spot.create_playlist(TEST_PL_NAME)
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


class TestEdit:
    def test_edit_details(self):

        name = TEST_PL_NAME
        description = "TEST DESCRIPTION 1"
        playlist = spot.create_playlist(
            name=name,
            public=False,
            collaborative=False,
            description=description,
        )
        item_id = playlist.id
        info = playlist.info

        assert playlist.name == TEST_PL_NAME
        assert info["description"] == description
        assert info["public"] == False
        assert info["collaborative"] == False

        new_name = "NEW_NAME"
        new_desc = "TEST DESCRIPTION 2"

        args = ["edit", "details", item_id, "--name", new_name]
        args += ["--description", new_desc]
        args += ["--public"]
        args += ["--collaborative"]
        result = runner.invoke(app, args=args)

        updated_pl = spot.get_item("playlist", item_id)
        spot.get_collection("playlist").remove(Playlist(spot.sp, item_id))

        info = updated_pl.info
        assert result.exit_code == 0
        assert updated_pl.name == new_name
        assert info["description"] == new_desc
        assert info["public"] == True
        assert info["collaborative"] == True

    def _modify_tracks_test(self, action, args, initial_tracks):
        item = spot.create_playlist(name="TEST_PLAYLIST_ADD_REMOVE")
        collection = FollowedPlaylists(spot.sp)

        if len(initial_tracks) > 0:
            spot.sp.playlist_add_items(item.id, initial_tracks)

        args = ["edit", action, item.id, *args]

        try:
            result = runner.invoke(app, args=args)
        except Exception as e:
            print(e)

        tracks = spot.sp.playlist_tracks(item.id)["items"]

        # cleanup
        collection.remove(item)

        assert result.exit_code == 0
        return tracks, result

    def test_add_track(self):
        init_tracks = ["55d553uqFMy1882OvdPPvV"]
        new_track = "3hgdCqTrU786DoKcqMGsA8"
        action, args = "add", [new_track]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)

        assert tracks[-1]["track"]["id"] == new_track

    def test_add_track_with_position(self):
        init_tracks = ["55d553uqFMy1882OvdPPvV"]
        new_track = "3hgdCqTrU786DoKcqMGsA8"
        action, args = "add", [new_track, "--insert-at", "0"]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)
        assert tracks[0]["track"]["id"] == new_track

    def test_add_track_no_dupe(self):
        init_tracks = ["3hgdCqTrU786DoKcqMGsA8"]
        new_track = "3hgdCqTrU786DoKcqMGsA8"
        action, args = "add", [new_track, "--add-if-unique"]
        tracks, result = self._modify_tracks_test(action, args, init_tracks)
        assert len(tracks) == 1
        assert Edit.Add.not_unique in result.stdout

    def test_add_multiple_tracks(self):
        init_tracks = []
        new_tracks = ["3hgdCqTrU786DoKcqMGsA8", "55d553uqFMy1882OvdPPvV"]
        action, args = "add", [*new_tracks]
        tracks, result = self._modify_tracks_test(action, args, init_tracks)
        assert len(tracks) == 2
        # assert "Tracks succesfully added!" in result.stdout

    def test_remove_track(self):
        init_tracks = ["55d553uqFMy1882OvdPPvV", "3hgdCqTrU786DoKcqMGsA8"]
        target_track = "3hgdCqTrU786DoKcqMGsA8"
        action, args = "remove", [target_track]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)
        assert tracks[-1]["track"]["id"] == "55d553uqFMy1882OvdPPvV"

    def test_remove_track_all(self):
        init_tracks = [
            "3hgdCqTrU786DoKcqMGsA8",
            "55d553uqFMy1882OvdPPvV",
            "3hgdCqTrU786DoKcqMGsA8",
        ]
        target_track = "3hgdCqTrU786DoKcqMGsA8"
        action, args = "remove", [target_track, "--all"]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)
        assert tracks[-1]["track"]["id"] == "55d553uqFMy1882OvdPPvV"
        assert tracks[0]["track"]["id"] == "55d553uqFMy1882OvdPPvV"
        assert len(tracks) == 1

    def test_remove_track_specific(self):
        init_tracks = [
            "3hgdCqTrU786DoKcqMGsA8",
            "55d553uqFMy1882OvdPPvV",
            "3hgdCqTrU786DoKcqMGsA8",
        ]
        target_track = "3hgdCqTrU786DoKcqMGsA8"
        action, args = "remove", [target_track, "--specific", "0,2"]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)
        assert tracks[-1]["track"]["id"] == "55d553uqFMy1882OvdPPvV"
        assert tracks[0]["track"]["id"] == "55d553uqFMy1882OvdPPvV"
        assert len(tracks) == 1

    def test_remove_track_using_offset(self):
        init_tracks = [
            "3hgdCqTrU786DoKcqMGsA8",
            "55d553uqFMy1882OvdPPvV",
            "3hgdCqTrU786DoKcqMGsA8",
        ]
        target_track = "3hgdCqTrU786DoKcqMGsA8"
        action, args = "remove", [target_track, "--offset", 1, -1]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)
        assert tracks[-1]["track"]["id"] == init_tracks[1]
        assert tracks[0]["track"]["id"] == init_tracks[0]
        assert len(tracks) == 2

    def test_remove_multiple_tracks(self):
        init_tracks = [
            "3hgdCqTrU786DoKcqMGsA8",
            "55d553uqFMy1882OvdPPvV",
            "6eXViRiXJKufjfzY3Ntxhx",
            "1c5aqW0BsVBWEiLS22xYys",
        ]
        target_tracks = ["3hgdCqTrU786DoKcqMGsA8", "1c5aqW0BsVBWEiLS22xYys"]
        action, args = "remove", [*target_tracks]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)
        assert tracks[0]["track"]["id"] == init_tracks[1]
        assert tracks[-1]["track"]["id"] == init_tracks[-2]
        assert len(tracks) == 2

    def test_remove_multiple_tracks_with_dupes(self):
        init_tracks = [
            "3hgdCqTrU786DoKcqMGsA8",
            "1c5aqW0BsVBWEiLS22xYys",
            "6eXViRiXJKufjfzY3Ntxhx",
            "3hgdCqTrU786DoKcqMGsA8",
            "55d553uqFMy1882OvdPPvV",
            "1c5aqW0BsVBWEiLS22xYys",
        ]
        target_tracks = ["3hgdCqTrU786DoKcqMGsA8", "1c5aqW0BsVBWEiLS22xYys"]
        action, args = "remove", [*target_tracks]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)
        assert tracks[0]["track"]["id"] == init_tracks[2]
        assert tracks[-1]["track"]["id"] == init_tracks[-1]
        assert len(tracks) == 4

    def test_remove_multiple_tracks_specific(self):
        init_tracks = [
            "1c5aqW0BsVBWEiLS22xYys",
            "55d553uqFMy1882OvdPPvV",
            "3hgdCqTrU786DoKcqMGsA8",
            "6eXViRiXJKufjfzY3Ntxhx",
            "3hgdCqTrU786DoKcqMGsA8",
            "1c5aqW0BsVBWEiLS22xYys",
            "3hgdCqTrU786DoKcqMGsA8",
        ]
        target_tracks = ["3hgdCqTrU786DoKcqMGsA8", "1c5aqW0BsVBWEiLS22xYys"]
        action, args = "remove", [*target_tracks, "--specific", "2,4; 0"]
        tracks, _ = self._modify_tracks_test(action, args, init_tracks)
        assert tracks[0]["track"]["id"] == init_tracks[1]
        assert tracks[-1]["track"]["id"] == init_tracks[-1]
        assert len(tracks) == 4
