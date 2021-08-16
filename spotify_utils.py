"""This module contains utility functions built on top of the spotipy wrapper"""
from typing import List
import spotipy
from decouple import config
from dummy_spotipy import DummySpotipy

USE_DUMMY_WRAPPER = config("USE_DUMMY_WRAPPER", cast=bool, default=False)

# Inherit from a dummy wrapper for fast local testing
BaseClass = DummySpotipy if USE_DUMMY_WRAPPER else spotipy.Spotify


class SpotifyExtended(BaseClass):
    """
    This class mostly contains functions for dealing with Spotify playlists.
    It might do more in the future.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def search_public_playlist(self, query, limit=10, market=None):
        """Search public playlists."""
        query = query.replace(" ", "+")
        results = self.search(
            q=query, limit=limit, offset=0, type="playlist", market=market
        )
        if results is not None:
            return results["playlists"]["items"]
        return []

    def create_playlist(
        self: spotipy.Spotify,
        name: str,
        public=False,
        collaborative=False,
        description="",
    ) -> str:
        """
        Attempts to create a playlist with the given name.
        Returns the playlist id if successful.
        """
        user_id = self.me()["id"]
        result = self.user_playlist_create(
            user_id,
            name=name,
            public=public,
            collaborative=collaborative,
            description=description,
        )
        return result["id"]

    def list_playlists(self: spotipy.Spotify) -> None:
        """Lists all of a users playlists"""
        user_id = self.me()["id"]
        playlists = self.user_playlists(user_id)
        for pl_list in playlists["items"]:
            print(pl_list["name"], pl_list["id"])

    def delete_playlist(self: spotipy.Spotify, pl_id: str) -> None:
        """Attempts to delete the playlist with the id 'pl_id'"""
        self.current_user_unfollow_playlist(playlist_id=pl_id)

    def delete_all(self: spotipy.Spotify, pl_name: str) -> None:
        """Attempts to delete all playlists with the same name"""
        playlists = self.get_playlist(pl_name=pl_name)
        if playlists is not None:
            for playlist in playlists:
                pl_id, pl_name = playlist["id"], playlist["name"]
                self.current_user_unfollow_playlist(playlist_id=pl_id)

    # I'd assume there is a better way to do this.
    # However, how many users are going to have > 100 playlists?
    # Not many. And even the outliers probably have < 1000 playlists.
    # Search in a linear fashion through < 1000 vaules is easy for a computer.
    # Might improve this at some point, but for now it's fine. TODO maybe.

    def check_exists(self: spotipy.Spotify, pl_id: str) -> bool:
        """Checks if a playlist exists."""
        playlist = self.get_playlist(pl_name=None, pl_id=pl_id)
        return playlist is not None

    def get_pl_id(self: spotipy.Spotify, pl_name: str) -> List[str]:
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
        self: spotipy.Spotify, pl_name: str = None, pl_id: str = None
    ) -> List[dict]:
        """
        Attempts to retrieve all info related to a given playlist.
        Accepts playlist name or id as ways of getting the playlist.
        Returns None if playlists does not exit

        Returns a list of dicts if the playlist exists (or multiple with the
        same name do).
        """
        user_id = self.me()["id"]
        playlists = self.user_playlists(user_id)
        selected_playlists = []
        for playlist in playlists["items"]:
            name, cur_id = playlist["name"], playlist["id"]
            if (
                pl_name is not None and name.strip() == pl_name.strip()
            ) or pl_id == cur_id:
                selected_playlists.append(playlist)

        return None if len(selected_playlists) == 0 else selected_playlists
