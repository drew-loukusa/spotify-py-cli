import textwrap
import spotipy
from interfaces import Followable, Utils

class Playlist(Followable, Utils):
    def __init__(self, sp: spotipy.Spotify, item_id: str, info = None):
        self.id = item_id
        self.sp = sp
        self.info = self._get_item() if info is None else info 
        self.name = None if self.info is None else self.info["name"]
        self.msg = ""

    def _get_item(self):
        try:
            return self.sp.playlist(self.id)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status != 404:
                raise e 
            else:
                self.msg = "Invalid Playlist ID"
                return None 

    def follow(self):
        self.sp.current_user_follow_playlist(playlist_id=self.id)

    def unfollow(self):
        self.sp.current_user_unfollow_playlist(playlist_id=self.id)

    def __repr__(self):
        info = self.info 
        pl_str = ["-----------------------"]
        pl_str += [f"Name:\t\t{info['name']}"]

        desc = info["description"]
        wrapped_desc = textwrap.wrap(
            "Description:\t" + desc,
            width=64,
            initial_indent="",
            subsequent_indent="\t\t",
        )
        pl_str.extend(wrapped_desc)
        pl_str += [f"Owner:\t\t{info['owner']['display_name']}"]
        pl_str += [f"Track count:\t{info['tracks']['total']}"]
        pl_str += [f"Playlist id:\t{info['id']}"]
        pl_str += [f"Owner id:\t{info['owner']['id']}"]
        pl_str += [f"Url: {info['external_urls']['spotify']}"]

        return "\n".join(pl_str)

    @staticmethod
    def get_followed_items(sp):
        playlists = []
        res = sp.current_user_playlists()
        if res is None:
            return None 
        for playlist in res["items"]:
            playlists.append(Playlist(sp, playlist["id"], info=playlist))
        return playlists

class Artist(Followable, Utils):
    def __init__(self, sp: spotipy.Spotify, item_id: str, info = None):
        self.id = item_id
        self.sp = sp
        self.info = self._get_item() if info is None else info 
        self.name = None if self.info is None else self.info["name"]
        self.msg = ""

    def _get_item(self):
        try:
            return self.sp.artist(self.id)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status != 404:
                raise e 
            else:
                self.msg = "Invalid Artist ID"
                return None 

    def follow(self):
        self.sp.user_follow_artists([self.id])

    def unfollow(self):
        self.sp.user_unfollow_artists([self.id])

    def __repr__(self):
        info = self.info 
        art_str = ["-----------------------"]
        art_str += [f"Name:\t\t{info['name']}"]
        art_str += [f"id:\t{info['id']}"]
        genres = info["genres"]
        wrapped_genres = textwrap.wrap(
            "Genres:\t" + ",".join(genres),
            width=64,
            initial_indent="",
            subsequent_indent="\t\t",
        )
        art_str.extend(wrapped_genres)
        art_str += [f"Followers: {info['followers']['total']}"]
        art_str += [f"Url: {info['external_urls']['spotify']}"]

        return "\n".join(art_str)

    @staticmethod
    def get_followed_items(sp):
        artists = []
        res = sp.current_user_followed_artists()
        if res is None: 
            return None 

        for artist in res["artists"]["items"]:
            artists.append(Artist(sp, artist["id"], artist))