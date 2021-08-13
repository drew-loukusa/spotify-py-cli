class DummySpotipy:
    def __init__(self):
        self.pl_id_count = 0
        self.data = {
            "id": "123_fake_user_id",
        }
        self.playlists = {"items": []}
        self.pl_dict = {}

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
        }
        self.playlists["items"].append(pl)
        result = {"id": pl_id}
        return result

    def user_playlists(self, user_id):
        return self.playlists

    def current_user_unfollow_playlist(self, playlist_id):
        name, id = None, None
        for pl in self.playlists["items"]:
            id = pl["id"]
            if id == playlist_id:
                break
        self.playlists["items"].remove(pl)
