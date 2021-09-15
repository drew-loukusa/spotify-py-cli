"""
This module contains classes used for managing a users library and followed content . 
All classes require a spotify instance for instantiation. 
All classes assume that the instance in question is configured to manage a user, 
i.e. the Auth Manager used was a SpotifyOAuth object, (or implicit grant?... TODO: Look into that)
"""
from spotipy import Spotify

from interfaces import Item, ItemCollection, Mutable
from items import Episode, Track, Artist, Album, Playlist, Show

class SavedEpisodes(ItemCollection, Mutable):
    """
    Class for managing the current user's saved episodes
    """

    def __init__(self, sp: Spotify):
        self.sp = sp

    @property
    def items(self):
        raise NotImplementedError
        self.sp.current_user_saved_episodes()

    def add(self, item: Episode):
        self.sp.current_user_saved_episodes_add(episodes=[item.id])

    def remove(self, item: Episode):
        self.sp.current_user_saved_episodes_delete(episodes=[item.id])

    def contains(self, item: Episode):
        return self.sp.current_user_saved_episodes_contains(episodes=[item.id])


class SavedTracks(ItemCollection, Mutable):
    """
    Class for managing the current user's saved tracks
    """

    def __init__(self, sp: Spotify):
        self.sp = sp

    @property
    def items(self):
        raise NotImplementedError

    def add(self, item: Track):
        self.sp.current_user_saved_tracks_add(tracks=[item.id])

    def remove(self, item: Track):
        self.sp.current_user_saved_tracks_delete(tracks=[item.id])

    def contains(self, item: Track):
        return self.sp.current_user_saved_tracks_contains(tracks=[item.id])


class SavedShows(ItemCollection, Mutable):
    """
    Class for managing the current user's saved shows
    """

    def __init__(self, sp: Spotify):
        self.sp = sp

    @property
    def items(self):
        raise NotImplementedError
        self.sp.current_user_saved_shows()

    def contains(self, item: Show):
        return self.sp.current_user_saved_shows_contains(shows=[item.id])

    def add(self, item: Show):
        self.sp.current_user_saved_shows_add(shows=[item.id])

    def remove(self, item: Item):
        self.sp.current_user_saved_shows_add(shows=[item.id])


class SavedAlbums(ItemCollection, Mutable):
    """
    Class for managing the current user's saved ablums
    """

    def __init__(self, sp: Spotify):
        self.sp = sp

    @property
    def items(self):
        albums = []
        res = self.sp.current_user_saved_albums()
        if res is None:
            return None

        for album in res["albums"]["items"]:
            albums.append(Album(self.sp, album["id"], album))

    def add(self, item: Album):
        self.sp.current_user_saved_albums_add(albums=[item.id])

    def remove(self, item: Album):
        self.sp.current_user_saved_albums_delete(albums=[item.id])

    def contains(self, item: Album):
        self.sp.current_user_saved_albums_contains(albums=[item.id])


class FollowedPlaylists(ItemCollection, Mutable):
    """
    Class for managing the current user's followed playlists
    """

    def __init__(self, sp: Spotify):
        self.sp = sp

    @property
    def items(self):
        playlists = []
        res = self.sp.current_user_playlists()
        if res is None:
            return None
        for playlist in res["items"]:
            playlists.append(Playlist(self.sp, playlist["id"], info=playlist))
        return playlists

    def add(self, item: Playlist):
        self.sp.current_user_follow_playlist(playlist_id=item.id)

    def remove(self, item: Playlist):
        self.sp.current_user_unfollow_playlist(playlist_id=item.id)

    def contains(self, item: Playlist):
        return self.sp.playlist_is_following(item.id, [self.sp.me()["id"]])[0]


class FollowedArtists(ItemCollection, Mutable):
    """
    Class for managing the current user's followed artists
    """

    def __init__(self, sp: Spotify):
        self.sp = sp

    @property
    def items(self):
        artists = []
        res = self.sp.current_user_followed_artists()
        if res is None:
            return None

        for artist in res["artists"]["items"]:
            artists.append(Artist(self.sp, artist["id"], artist))

    def add(self, item: Artist):
        self.sp.user_follow_artists([item.id])

    def remove(self, item: Artist):
        self.sp.user_unfollow_artists([item.id])

    def contains(self, item: Artist):
        return self.sp.current_user_following_artists([item.id])[0]