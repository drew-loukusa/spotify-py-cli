"""This module contains a facade class built on top of spotipy Spotify wrapper"""
from typing import List
import spotipy
from decouple import config
from spotipy.oauth2 import SpotifyOAuth
from concrete import Playlist, Artist
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

# Playlist and Artist currently implement followable.
# More possible interfaces... Editable, Searchable
# If I want to add more interfaces, I should formally define each one using the ABC module, so that
# I can denote with multiple inheritance which interfaces each item implements


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
        self.types = {"playlist": Playlist, "artist": Artist}

    def get_item(self, item_type, item_id):
        return self.types[item_type](self.sp, item_id)

    def get_followed_items(self, item_type):
        item_class = self.types[item_type]
        return item_class.get_followed_items(self.sp)

    def get_followed_item(
        self, item_type: str, item_name: str = None, item_id: str = None
    ) -> List[dict]:
        item_class = self.types[item_type]
        items = item_class.get_followed_items(self.sp)
        selected_items = []
        for item in items:
            name, cur_id = item.name, item.id
            if (
                item_name is not None and name.strip() == item_name.strip()
            ) or item_id == cur_id:
                selected_items.append(item)

        return None if len(selected_items) == 0 else selected_items

    def get_unfollowed_item():
        # This can be a seperate function, or you can make this an argument of 'get_followed_item' and rename it back to 'get_item'
        # Getting an item for unfollowing means get the item from the user's followed itmes
        # gettting an item for following means searching the publicly available items
        pass

    def search_public(self, item_type, query, limit=10, offset=0, market=None):
        raw_items = self.sp.search(query, limit, offset, item_type, market)
        items = []
        for raw_item in raw_items[item_type + "s"]["items"]:
            if raw_item is None:
                continue
            item_id = raw_item["id"]
            items.append(self.types[item_type](self.sp, item_id, info=raw_item))
        return items

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

    @staticmethod
    def print_items(print_func, items):
        for item in items:
            print_func(item)
