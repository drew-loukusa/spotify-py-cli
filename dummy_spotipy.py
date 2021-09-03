""" 
This module contains a dummy wrapper used for local testing. 
The dummy wrapper emulates some behavior of the spotipy Spotify API wrapper.
"""


class DummySpotipy:
    def __init__(self, auth_manager=None):
        self.pl_id_count = 0
        self.data = {
            "id": "123_fake_user_id",
        }
        self.playlists = {"items": []}
        self.non_followed_playlists = {"items": []}
        self.pl_dict = {}

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
        self.non_followed_playlists["items"].append(pl)

    def me(self):
        return self.data

    def user_playlist_create(
        self,
        user_id,
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
        self.playlists["items"].append(pl)
        result = {"id": pl_id}
        return result

    def user_playlists(self, user_id):
        return self.playlists

    def current_user_follow_playlist(self, playlist_id):
        playlist = None
        for pl in self.non_followed_playlists["items"]:
            pl_id = pl["id"]
            if pl_id == playlist_id:
                playlist = pl
                break
        self.playlists["items"].append(playlist)
        self.non_followed_playlists["items"].remove(playlist)

    def current_user_unfollow_playlist(self, playlist_id):
        playlist = None
        for pl in self.playlists["items"]:
            pl_id = pl["id"]
            if pl_id == playlist_id:
                playlist = pl
                break
        if playlist is not None:
            self.playlists["items"].remove(playlist)

    def search(self, q, limit=10, offset=0, type="", market=None):
        return {"playlists": self.playlists}

    def playlist_is_following(self, playlist_id, user_ids):
        for pl in self.playlists["items"]:
            pl_id = pl["id"]
            if pl_id == playlist_id:
                return [True]
        return [False]
