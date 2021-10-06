"""This module contains a facade class built on top of spotipy Spotify wrapper"""
from typing import List

import spotipy
from decouple import config
from spotipy.oauth2 import SpotifyOAuth

from cli.facade.interfaces import Item, ItemCollection

from cli.facade.items import Artist, Playlist, Track, Album, Episode, Show
from cli.facade.user_libary import (
    FollowedArtists,
    FollowedPlaylists,
    SavedTracks,
    SavedAlbums,
    SavedEpisodes,
    SavedShows,
)
from tests.dummy_spotipy import DummySpotipy

USE_DUMMY_WRAPPER = config("USE_DUMMY_WRAPPER", cast=bool, default=False)
SCOPE = "playlist-modify-private \
            user-follow-read \
            user-follow-modify \
            user-library-read \
            user-library-modify \
            playlist-read-private \
            playlist-read-collaborative \
            playlist-modify-public"


# If testing locally, use the dummy wrapper
SpotifyWrapper = DummySpotipy if USE_DUMMY_WRAPPER else spotipy.Spotify


class SpotipySpotifyFacade:
    """
    A facade for simplifying interaction with spotipy's Spotify object.
    """

    def __init__(self, output_object=None):
        """
        output_object: Optional, any function capable of printing text. If configured with an object, this is where the facade will send output.
        """
        self.sp = SpotifyWrapper(
            auth_manager=SpotifyOAuth(
                client_id=config("SPOTIPY_CLIENT_ID"),
                client_secret=config("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=config("SPOTIPY_REDIRECT_URI"),
                scope=SCOPE,
            )
        )
        self.user_id = self.sp.me()["id"]
        self.types = {
            "playlist": {"item": Playlist, "collection": FollowedPlaylists},
            "artist": {"item": Artist, "collection": FollowedArtists},
            "track": {"item": Track, "collection": SavedTracks},
            "album": {"item": Album, "collection": SavedAlbums},
            "episode": {"item": Episode, "collection": SavedEpisodes},
            "show": {"item": Show, "collection": SavedShows},
        }
        self.output = output_object

    def get_item(self, item_type: str, item_id: str) -> Item:
        """
        Returns an Item given item_type and item_id.
        See self.types for list of supported 'item_type's
        """
        return self.types[item_type]["item"](self.sp, item_id)

    def get_collection(self, item_type: str) -> ItemCollection:
        """
        Returns an ItemCollection given item_type and item_id.
        See self.types for list of supported 'item_type's
        """
        i_type = self.types[item_type]
        if "collection" in i_type:
            return i_type["collection"](self.sp)
        else:
            return None

    def get_followed_items(self, item_type):
        item_class = self.types[item_type]["collection"](self.sp)
        return item_class.items()

    def get_followed_item(
        self, item_type: str, item_name: str = None, item_id: str = None
    ) -> List[dict]:
        item_class = self.types[item_type]["collection"](self.sp)
        selected_items = []
        for item in item_class.items():
            name, cur_id = item.name, item.id
            if (
                item_name is not None and name.strip() == item_name.strip()
            ) or item_id == cur_id:
                selected_items.append(item)

        return None if len(selected_items) == 0 else selected_items

    def get_item_and_collection(self, item_type: str, item_id: str):
        """
        Get an Item object and an ItemCollection object base on item_type and item_id.
        Checks to see if the item exists, and if item_type is valid.

        Sends error messages to self.output, if configured.

        If successful, returns two objects, otherwise returns None
        """
        item = self.get_item(item_type, item_id)
        collection = self.get_collection(item_type)

        # Check that item_type is valid
        if collection is None:
            if self.output is not None:
                self.output(f"Item of type '{item_type}' not recognized!")
            return None, None

        # Check if the given item_id corresponds to an actual item
        if item.info is None:
            if self.output is not None:
                self.output(f"No {item_type} exists with id: {item_id}")
            return None, None

        return item, collection

    def search_public(self, item_type, query, limit=10, offset=0, market=None):
        raw_items = self.sp.search(query, limit, offset, item_type, market)
        init_item = self.types[item_type]["item"]
        items = []
        for raw_item in raw_items[item_type + "s"]["items"]:
            if raw_item is None:
                continue
            item_id = raw_item["id"]
            items.append(init_item(self.sp, item_id, info=raw_item))
        return items

    def create_playlist(
        self,
        name: str,
        public=False,
        collaborative=False,
        description="",
    ) -> Playlist:
        """
        Attempts to create a playlist with the given name.
        Returns a Playlist object if succesful, None if not.
        """
        result = self.sp.user_playlist_create(
            user=self.user_id,
            name=name,
            public=public,
            collaborative=collaborative,
            description=description,
        )
        if result is not None:
            playlist = self.get_item("playlist", result["id"])
            return playlist
        return None

    @staticmethod
    def print_items(print_func, items):
        for item in items:
            print_func("-----------------------------")
            print_func(item)
