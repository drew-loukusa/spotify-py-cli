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

    def follow_item(self, item_type, item_id):
        """
        Follows a followable item.
        item_type: "playlist" or "artist"
        """
        if item_type == "playlist":
            return self.follow_playlist(pl_id=item_id)
        elif item_type == "artist":
            return self.follow_artist(artist_id=item_id)

    def unfollow_item(self, item_type, item_id):
        """
        Unfollows a followable item.
        item_type: "playlist" or "artist"
        """
        if item_type == "playlist":
            return self.unfollow_playlist(pl_id=item_id)
        elif item_type == "artist":
            return self.unfollow_artist(artist_id=item_id)

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

    # ========================== Playlists ===================================#
    def get_user_playlists(self):
        """Gets all of a users playlists"""
        res = self.sp.user_playlists(self.user_id)
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
        return self.sp.playlist_is_following(playlist_id, [self.user_id])[0]

    def follow_playlist(self, pl_id):
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

    def get_item(
        self, item_type: str, item_name: str = None, item_id: str = None
    ) -> List[dict]:
        if item_type == "playlist":
            return self.get_playlist(item_name, item_id)
        elif item_type == "artist":
            return self.get_artist(item_name, item_id)

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
