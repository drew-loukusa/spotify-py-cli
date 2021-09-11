"""This module contains a facade class built on top of spotipy Spotify wrapper"""
import textwrap
from typing import List
import spotipy
from decouple import config
from spotipy.oauth2 import SpotifyOAuth
from dummy_spotipy import DummySpotipy

USE_DUMMY_WRAPPER = config("USE_DUMMY_WRAPPER", cast=bool, default=False)
SCOPE = "playlist-modify-private \
            user-follow-read \
            user-follow-modify \
            playlist-read-private \
            playlist-read-collaborative \
            playlist-modify-public"


# If testing locally, use the dummy wrapper
SpotifyWrapper = DummySpotipy if USE_DUMMY_WRAPPER else spotipy.Spotify


class Playlist:
    def __init__(self, sp: spotipy.Spotify, item_id: str):
        self.sp = sp
        self.info = sp.playlist(item_id)
        self.id = item_id
        self.name = self.info["name"]

    def follow(self):
        self.sp.current_user_follow_playlist(playlist_id=self.id)

    def unfollow(self):
        self.sp.current_user_unfollow_playlist(playlist_id=self.id)

    def __repr__(self):
        """Extract relevant info about a playlist from the dict 'playlist' as a string"""
        info = ["-----------------------"]
        info += [f"Name:\t\t{self.info['name']}"]

        desc = self.info["description"]
        wrapped_desc = textwrap.wrap(
            "Description:\t" + desc,
            width=64,
            initial_indent="",
            subsequent_indent="\t\t",
        )
        info.extend(wrapped_desc)
        info += [f"Owner:\t\t{self.info['owner']['display_name']}"]
        info += [f"Track count:\t{self.info['tracks']['total']}"]
        info += [f"Playlist id:\t{self.info['id']}"]
        info += [f"Owner id:\t{self.info['owner']['id']}"]
        info += [f"Url: {self.info['external_urls']['spotify']}"]

        return "\n".join(info)

    @staticmethod
    def get_followed_item(sp, item_name: str = None, item_id: str = None):
        playlists = sp.current_user_playlists()
        selected_playlists = []
        for playlist in playlists["items"]:
            item_name, cur_id = playlist["name"], playlist["id"]
            if (
                item_name is not None and item_name.strip() == item_name.strip()
            ) or item_id == cur_id:
                selected_playlists.append(Playlist(sp, cur_id))

        return None if len(selected_playlists) == 0 else selected_playlists


class Artist:
    def __init__(self, sp: spotipy.Spotify, item_id: str):
        self.sp = sp
        self.info = sp.artist(item_id)
        self.id = item_id
        self.name = self.info["name"]

    def follow(self):
        self.sp.user_follow_artists([self.id])

    def unfollow(self):
        self.sp.user_unfollow_artists([self.id])

    def __repr__(self):
        """Extract relevant info about a artist from the dict 'artist' as a string"""
        info = ["-----------------------"]
        info += [f"Name:\t\t{self.info['name']}"]
        info += [f"id:\t{self.info['id']}"]
        genres = self.info["genres"]
        wrapped_genres = textwrap.wrap(
            "Genres:\t" + ",".join(genres),
            width=64,
            initial_indent="",
            subsequent_indent="\t\t",
        )
        info.extend(wrapped_genres)
        info += [f"Followers: {self.info['followers']['total']}"]
        info += [f"Url: {self.info['external_urls']['spotify']}"]

        return "\n".join(info)

    @staticmethod
    def get_followed_item(
        sp, item_name: str = None, item_id: str = None
    ) -> List[dict]:
        selected_artists = []
        artists = sp.current_user_followed_artists()
        for artist in artists["artists"]["items"]:
            cur_name, cur_id = artist["name"], artist["id"]
            if (
                item_name is not None and item_name.rstrip() == cur_name.strip()
            ) or item_id == cur_id:
                selected_artists.append(Artist(sp, cur_id))

        return None if len(selected_artists) == 0 else selected_artists


class SpotipySpotifyFacade:
    """
    A facade for simplifying interaction with spotipy's Spotify object.
    """

    def __init__(self):
        self.sp = SpotifyWrapper(
            auth_manager=SpotifyOAuth(
                client_id=config("SPOTIPY_CLIENT_ID"),
                client_secret=config("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=config("SPOTIPY_REDIRECT_URI"),
                scope=SCOPE,
            )
        )
        self.user_id = self.sp.me()["id"]
        self.followables = {"playlist": Playlist, "artist": Artist}

    def get_followable_instance(self, item_type, item_id):
        return self.followables[item_type](self.sp, item_id)

    def search_public_playlist(self, query, limit=10, market=None):
        """Search public playlists."""
        query = query.replace(" ", "+")
        results = self.sp.search(
            q=query, limit=limit, offset=0, type="playlist", market=market
        )
        if results is not None:
            return results["playlists"]["items"]
        return []

    def create_playlist(
        self,
        name: str,
        public=False,
        collaborative=False,
        description="",
    ) -> str:
        """
        Attempts to create a playlist with the given name.
        Returns the playlist id if successful.
        """
        result = self.sp.user_playlist_create(
            user=self.user_id,
            name=name,
            public=public,
            collaborative=collaborative,
            description=description,
        )
        return result["id"]

    def follow_artist(self, artist_id):
        """
        Follows artist with ID 'artist_id'
        Returns name of followed artist
        """
        self.sp.user_follow_artists([artist_id])
        return self.sp.artist(artist_id)["name"]

    def unfollow_artist(self, artist_id):
        """
        Unfollows artist with ID 'artist_id'
        Returns name of followed artist
        """
        name = self.sp.artist(artist_id)["name"]
        self.sp.user_unfollow_artists([artist_id])
        return name

    def get_user_items(self, item_type):
        if item_type == "playlist":
            return self.get_user_playlists()
        elif item_type == "artist":
            return self.get_user_artists()

    def get_user_playlists(self):
        """Gets all of a users followed playlists"""
        res = self.sp.user_playlists(self.user_id)
        if res is not None:
            return res["items"]
        return res

    def get_user_artists(self):
        """Gets all of a users follewed artists"""
        res = self.sp.current_user_followed_artists()
        if res is not None:
            return res["artists"]["items"]
        return res

    def list_playlists(self) -> None:
        """Lists all of a users playlists"""

        playlists = self.get_user_playlists()
        if playlists is not None:
            for pl_list in playlists:
                print(pl_list["name"], pl_list["id"])

    def following_playlist(self, playlist_id):
        return self.sp.playlist_is_following(playlist_id, [self.user_id])[0]

    def follow_playlist(self, pl_id):
        """
        Follows playlist with id 'pl_id'
        Returns name of playlist followed
        """
        self.sp.current_user_follow_playlist(playlist_id=pl_id)
        name = self.get_playlist(pl_id=pl_id)[0]["name"]
        return name

    def unfollow_playlist(self, pl_id: str) -> None:
        """Attempts to unfollow the playlist with the id 'pl_id'"""
        self.sp.current_user_unfollow_playlist(playlist_id=pl_id)

    def unfollow_all_pl(self, pl_name: str) -> None:
        """Attempts to unfollow all playlists with the same name"""
        playlists = self.get_playlist(pl_name=pl_name)
        if playlists is not None:
            for playlist in playlists:
                pl_id, pl_name = playlist["id"], playlist["name"]
                self.sp.current_user_unfollow_playlist(playlist_id=pl_id)

    def check_exists(self, pl_id: str) -> bool:
        """Checks if a playlist exists."""
        playlist = self.get_playlist(pl_name=None, pl_id=pl_id)
        return playlist is not None

    def get_pl_id(self, pl_name: str) -> List[str]:
        """
        Gets the id of a playlist(s) given a name.
        Returns None if playlist does not exist.

        Returns list of id strings if 1 or more playlists exist with given name.
        """
        id_list = []
        playlists = self.get_playlist(pl_name=pl_name)
        if playlists is not None:
            for pl_list in playlists:
                id_list.append(pl_list["id"])
            return id_list
        return None

    def get_followed_item(
        self, item_type: str, item_name: str = None, item_id: str = None
    ) -> List[dict]:
        item = self.followables[item_type]
        return item.get_followed_item(self.sp, item_name, item_id)

    def get_unfollowed_item():
        # This can be a seperate function, or you can make this an argument of 'get_followed_item' and rename it back to 'get_item'
        # Getting an item for unfollowing means get the item from the user's followed itmes
        # gettting an item for following means searching the publicly available items
        pass

    def get_playlist(
        self, pl_name: str = None, pl_id: str = None
    ) -> List[dict]:
        """
        Attempts to retrieve a given playlist that the user is following.
        Accepts playlist name or id as ways of getting the playlist.
        Returns None if playlist is not being followed by the user

        Returns a list of dicts if the playlist exists (or multiple with the
        same name do).
        """
        playlists = self.sp.user_playlists(self.user_id)
        selected_playlists = []
        for playlist in playlists["items"]:
            name, cur_id = playlist["name"], playlist["id"]
            if (
                pl_name is not None and name.strip() == pl_name.strip()
            ) or pl_id == cur_id:
                selected_playlists.append(playlist)

        return None if len(selected_playlists) == 0 else selected_playlists

    def get_artist(self, name: str = None, artist_id: str = None) -> List[dict]:
        selected_artists = []
        artists = self.sp.current_user_followed_artists()
        for artist in artists["artists"]["items"]:
            cur_name, cur_id = artist["name"], artist["id"]
            if (
                name is not None and name.rstrip() == cur_name.strip()
            ) or artist_id == cur_id:
                selected_artists.append(artist)

        return None if len(selected_artists) == 0 else selected_artists

    @staticmethod
    def stringify_playlist(playlist) -> str:
        """Extract relevant info about a playlist from the dict 'playlist' as a string"""
        info = ["-----------------------"]
        info += [f"Name:\t\t{playlist['name']}"]

        desc = playlist["description"]
        wrapped_desc = textwrap.wrap(
            "Description:\t" + desc,
            width=64,
            initial_indent="",
            subsequent_indent="\t\t",
        )
        info.extend(wrapped_desc)
        info += [f"Owner:\t\t{playlist['owner']['display_name']}"]
        info += [f"Track count:\t{playlist['tracks']['total']}"]
        info += [f"Playlist id:\t{playlist['id']}"]
        info += [f"Owner id:\t{playlist['owner']['id']}"]
        info += [f"Url: {playlist['external_urls']['spotify']}"]

        return "\n".join(info)

    @staticmethod
    def stringify_artist(artist) -> str:
        """Extract relevant info about a artist from the dict 'artist' as a string"""
        info = ["-----------------------"]
        info += [f"Name:\t\t{artist['name']}"]
        info += [f"id:\t{artist['id']}"]
        genres = artist["genres"]
        wrapped_genres = textwrap.wrap(
            "Genres:\t" + ",".join(genres),
            width=64,
            initial_indent="",
            subsequent_indent="\t\t",
        )
        info.extend(wrapped_genres)
        info += [f"Followers: {artist['followers']['total']}"]
        info += [f"Url: {artist['external_urls']['spotify']}"]

        return "\n".join(info)

    @staticmethod
    def print_playlists(print_func, playlists):
        if playlists is None:
            print_func("No playlists to print!")
            return

        for pl_list in playlists:
            if type(pl_list) is Playlist:
                print_func(pl_list)
            else:
                print_func(SpotipySpotifyFacade.stringify_playlist(pl_list))

    @staticmethod
    def print_artists(print_func, artists):
        if artists is None:
            print_func("No artists to print!")
            return

        for artist in artists:
            print_func(SpotipySpotifyFacade.stringify_artist(artist))

    @staticmethod
    def print_items(item_type, print_func, items):
        if item_type == "playlist":
            SpotipySpotifyFacade.print_playlists(print_func, items)
        elif item_type == "artist":
            SpotipySpotifyFacade.print_artists(print_func, items)
