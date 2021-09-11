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
        self.artists = {"artists": {"items": []}}
        self.non_followed_artists = {}
        self.playlists = {"items": []}
        self.non_followed_playlists = {"items": []}
        self.pl_dict = {}

    def current_user_following_artists(self, ids):
        bools = []
        for item_id in ids:
            for artist in self.artists["artists"]["items"]:
                if item_id == artist["id"]:
                    bools.append(True)
                    break
            else:
                bools.append(False)
        return bools

    def current_user_followed_artists(self):
        return self.artists

    def artist(self, artist_id):
        for art_id, name in self.non_followed_artists.items():
            if artist_id == art_id:
                return {"name": name, "id": art_id}

        for artist in self.artists["artists"]["items"]:
            if artist_id == artist["id"]:
                return artist

    def user_follow_artists(self, ids):
        for artist_id in ids:
            if artist_id in self.non_followed_artists:
                name = self.non_followed_artists.pop(artist_id)
                self.artists["artists"]["items"].append(
                    {"name": name, "id": artist_id}
                )

    def user_unfollow_artists(self, ids):
        remove = []
        for artist_id in ids:
            for i, artist in enumerate(self.artists["artists"]["items"]):
                if artist_id == artist["id"]:
                    remove.append(i)

        for index in remove:
            self.artists["artists"]["items"].pop(index)

    def create_non_followed_artist(self, item_id, name=None):
        self.non_followed_artists[item_id] = name

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
        self.playlists["items"].append(pl)
        result = {"id": pl_id}
        return result

    def user_playlists(self, user):
        return self.playlists

    def current_user_playlists(self):
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

    def playlist(self, playlist_id):
        for pl in self.playlists["items"]:
            pl_id = pl["id"]
            if pl_id == playlist_id:
                return pl

        for pl in self.non_followed_playlists["items"]:
            pl_id = pl["id"]
            if pl_id == playlist_id:
                return pl

        return None
