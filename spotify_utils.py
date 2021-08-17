"""This module contains utility functions built on top of the spotipy wrapper"""
import textwrap
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
        user_id = self.me()["id"]
        result = self.user_playlist_create(
            user_id,
            name=name,
            public=public,
            collaborative=collaborative,
            description=description,
        )
        return result["id"]

    def get_user_playlists(self):
        """Gets all of a users playlists"""
        user_id = self.me()["id"]
        res = self.user_playlists(user_id)
        if res is not None:
            return res["items"]
        return res

    def list_playlists(self) -> None:
        """Lists all of a users playlists"""

        playlists = self.get_user_playlists()
        if playlists is not None:
            for pl_list in playlists:
                print(pl_list["name"], pl_list["id"])

    def following_playlist(self, playlist_id):
        return self.playlist_is_following(playlist_id, [self.me()["id"]])[0]

    def unfollow_playlist(self, pl_id: str) -> None:
        """Attempts to unfollow the playlist with the id 'pl_id'"""
        self.current_user_unfollow_playlist(playlist_id=pl_id)

    def unfollow_all_pl(self, pl_name: str) -> None:
        """Attempts to unfollow all playlists with the same name"""
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

    def get_playlist(self, pl_name: str = None, pl_id: str = None) -> List[dict]:
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
    def print_playlists(print_function, playlists):
        if playlists is None:
            print_function("No playlists to print!")
            return

        for pl_list in playlists:
            print_function(SpotifyExtended.stringify_playlist(pl_list))
