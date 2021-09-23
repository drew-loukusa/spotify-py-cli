""" 
This module contains a dummy wrapper used for local testing. 
The dummy wrapper emulates some behavior of the spotipy Spotify API wrapper.
"""
from items import Show
from typing import List


class DummySpotipy:
    def __init__(self, auth_manager=None):
        self.pl_id_count = 0
        self.data = {
            "id": "123_fake_user_id",
        }

        self.items = {
            "artist": {"items": []},
            "album": {"items": []},
            "track": {"items": []},
            "episode": {"items": []},
            "show": {"items": []},
            "playlist": {"items": []},
        }
        self.ext_items = {
            "artist": {"items": []},
            "album": {"items": []},
            "track": {"items": []},
            "episode": {"items": []},
            "show": {"items": []},
            "playlist": {"items": []},
        }

    # ============================= General ===================================#

    def me(self):
        return self.data

    def search(self, q, limit=10, offset=0, type="", market=None):
        return {"playlists": self.items["playlist"]}

    def create_item(
        self,
        item_type,
        item_id,
        item_name,
        extern=False,
        additional_properties: dict = None,
    ):
        collection = self.items
        if extern:
            collection = self.ext_items

        item = {"name": item_name, "id": item_id}
        if additional_properties is not None:
            item.update(additional_properties)

        collection[item_type]["items"].append(item)

    def select_item(self, item_type, item_id, extern: int = 0):
        """
        extern: 0 = search user collection, 1 = search public (external) collection, 2 = search both
        """
        item = None
        collection = self.items[item_type]["items"]
        if extern == 1:
            collection = self.ext_items[item_type]["items"]
        elif extern == 2:
            collection.extend(self.ext_items[item_type]["items"])

        for cur_item in collection:
            cur_id = cur_item["id"]
            if cur_id == item_id:
                item = cur_item
                break
        return item

    def add_item(self, item_type, item_id):
        item = self.select_item(item_type, item_id, extern=1)
        self.items[item_type]["items"].append(item)
        self.ext_items[item_type]["items"].remove(item)

    def remove_item(self, item_type, item_id):
        item = self.select_item(item_type, item_id, extern=0)
        self.ext_items[item_type]["items"].append(item)
        self.items[item_type]["items"].remove(item)

    def contains(self, item_type, item_id, extern=0):
        item = self.select_item(
            item_type=item_type, item_id=item_id, extern=extern
        )
        return item is not None

    # ============================= Artists ===================================#

    def current_user_following_artists(self, ids: List[str]):
        bools = []
        for item_id in ids:
            for artist in self.items["artist"]["items"]:
                if item_id == artist["id"]:
                    bools.append(True)
                    break
            else:
                bools.append(False)
        return bools

    def current_user_followed_artists(self, limit=20):
        return {"artists": self.items["artist"]}

    def artist(self, artist_id):
        all_artists = (
            self.items["artist"]["items"] + self.ext_items["artist"]["items"]
        )
        for artist in all_artists:
            if artist_id == artist["id"]:
                return artist

    def user_follow_artists(self, ids):
        for artist_id in ids:
            self.add_item(item_type="artist", item_id=artist_id)

    def user_unfollow_artists(self, ids):
        for artist_id in ids:
            self.remove_item(item_type="artist", item_id=artist_id)

    def create_non_followed_artist(self, item_id, name=None):
        nf_artist = {"name": name, "id": item_id}
        self.ext_items["artist"]["items"].append(nf_artist)

    # ============================ Playlists ==================================#

    def create_non_followed_playlist(self, name, id=None):
        pl_id = "123_fake_playlist_id" + str(self.pl_id_count)
        if id is not None:
            pl_id = id
        self.pl_id_count += 1
        pl = {
            "name": name,
            "id": pl_id,
            "public": "False",
            "collaborative": "False",
            "description": "No description.",
            "tracks": {"total": self.pl_id_count},
            "owner": {
                "display_name": f"test_owner_name{self.pl_id_count}",
                "id": f"test_owner_id{self.pl_id_count}",
            },
            "external_urls": {
                "spotify": f"test_external_url{self.pl_id_count}.com"
            },
        }
        self.ext_items["playlist"]["items"].append(pl)

    def user_playlist_create(
        self,
        user,
        name,
        public,
        collaborative,
        description,
    ):
        pl_id = "123_fake_playlist_id" + str(self.pl_id_count)
        self.pl_id_count += 1
        pl = {
            "name": name,
            "id": pl_id,
            "public": public,
            "collaborative": collaborative,
            "description": description,
            "tracks": {"total": self.pl_id_count},
            "owner": {
                "display_name": f"test_owner_name{self.pl_id_count}",
                "id": f"test_owner_id{self.pl_id_count}",
            },
            "external_urls": {
                "spotify": f"test_external_url{self.pl_id_count}.com"
            },
        }
        self.items["playlist"]["items"].append(pl)
        return {"id": pl_id}

    def user_playlists(self, user):
        return self.items["playlist"]

    def current_user_playlists(self, limit=20, offset=0):
        stuff = {"next": None}
        stuff.update(self.items["playlist"])
        return stuff

    def current_user_follow_playlist(self, playlist_id):
        self.add_item(
            item_type="playlist",
            item_id=playlist_id,
        )

    def current_user_unfollow_playlist(self, playlist_id):
        self.remove_item(item_type="playlist", item_id=playlist_id)

    def playlist_is_following(self, playlist_id, user_ids):
        return [self.contains("playlist", playlist_id)]

    def playlist(self, playlist_id):
        item = self.select_item("playlist", playlist_id, extern=0)
        if item is not None:
            return item

        return self.select_item("playlist", playlist_id, extern=1)

    # ============================== Albums ===================================#
    def album(self, album_id):
        return self.select_item("album", album_id, extern=1)

    def current_user_saved_albums_contains(self, albums: List[str]):
        return [self.contains("album", albums[0], extern=0)]

    def current_user_saved_albums_add(self, albums: List[str]):
        self.add_item("album", albums[0])

    def current_user_saved_albums_delete(self, albums: List[str]):
        self.remove_item("album", albums[0])

    # ============================== Shows ====================================#
    def show(self, show_id):
        return self.select_item("show", show_id, extern=1)

    def current_user_saved_shows_contains(self, shows: List[str]):
        return [self.contains("show", shows[0], extern=0)]

    def current_user_saved_shows_add(self, shows: List[str]):
        self.add_item("show", shows[0])

    def current_user_saved_shows_delete(self, shows: List[str]):
        self.remove_item("show", shows[0])

    # ============================= Episodes ==================================#
    def episode(self, ep_id):
        return self.select_item("episode", ep_id, extern=1)

    def current_user_saved_episodes_contains(self, episodes: List[str]):
        """episodes: list of id's"""
        return [self.contains("episode", episodes[0], extern=0)]

    def current_user_saved_episodes_add(self, episodes: List[str]):
        self.add_item("episode", episodes[0])

    def current_user_saved_episodes_delete(self, episodes: List[str]):
        self.remove_item("episode", episodes[0])

    # ============================== Tracks ===================================#
    def track(self, track_id):
        return self.select_item("track", track_id, extern=1)

    def current_user_saved_tracks_contains(self, tracks: List[str]):
        return [self.contains("track", tracks[0], extern=0)]

    def current_user_saved_tracks_add(self, tracks: List[str]):
        self.add_item("track", tracks[0])

    def current_user_saved_tracks_delete(self, tracks: List[str]):
        self.remove_item("track", tracks[0])
