"""
This module contains classes used for managing a users library and followed content . 
All classes require a spotify instance for instantiation. 
All classes assume that the instance in question is configured to manage a user, 
i.e. the Auth Manager used was a SpotifyOAuth object, (or implicit grant?... TODO: Look into that)
"""
from typing import List

from spotipy import Spotify

from cli.interfaces import Item, ItemCollection, Mutable
from cli.items import Episode, Track, Artist, Album, Playlist, Show


class SavedEpisodes(ItemCollection, Mutable):
    """
    Class for managing the current user's saved episodes
    """

    def __init__(self, sp: Spotify):
        self.sp: Spotify = sp

    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Episode]:
        raw_episodes = self._items(
            self.sp.current_user_saved_episodes,
            limit=limit,
            offset=offset,
            retrieve_all=retrieve_all,
        )
        if raw_episodes is None:
            return None

        episodes = []
        for episode in raw_episodes:
            ep = episode["episode"]
            episodes.append(Episode(self.sp, ep["id"], ep))
        return episodes

    def add(self, item: Episode, **kwargs):
        self.sp.current_user_saved_episodes_add(episodes=[item.id])

    def remove(self, item: Episode, **kwargs):
        self.sp.current_user_saved_episodes_delete(episodes=[item.id])

    def contains(self, item: Episode):
        return self.sp.current_user_saved_episodes_contains(episodes=[item.id])[
            0
        ]


class SavedTracks(ItemCollection, Mutable):
    """
    Class for managing the current user's saved tracks
    """

    def __init__(self, sp: Spotify):
        self.sp: Spotify = sp

    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Track]:
        raw_tracks = self._items(
            self.sp.current_user_saved_tracks,
            limit=limit,
            offset=offset,
            retrieve_all=retrieve_all,
        )
        if raw_tracks is None:
            return None

        tracks = []
        for track in tracks:
            track = track["track"]
            tracks.append(Track(self.sp, track["id"], track))
        return tracks

    def add(self, item: Track, **kwargs):
        self.sp.current_user_saved_tracks_add(tracks=[item.id])

    def remove(self, item: Track, **kwargs):
        self.sp.current_user_saved_tracks_delete(tracks=[item.id])

    def contains(self, item: Track):
        return self.sp.current_user_saved_tracks_contains(tracks=[item.id])[0]


class SavedShows(ItemCollection, Mutable):
    """
    Class for managing the current user's saved shows
    """

    def __init__(self, sp: Spotify):
        self.sp: Spotify = sp

    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Show]:
        raw_shows = self._items(
            self.sp.current_user_saved_shows,
            limit=limit,
            offset=offset,
            retrieve_all=retrieve_all,
        )
        if raw_shows is None:
            return None

        shows = []
        for show in raw_shows:
            show = show["show"]
            shows.append(Show(self.sp, show["id"], show))
        return shows

    def contains(self, item: Show):
        return self.sp.current_user_saved_shows_contains(shows=[item.id])[0]

    def add(self, item: Show, **kwargs):
        self.sp.current_user_saved_shows_add(shows=[item.id])

    def remove(self, item: Item, **kwargs):
        self.sp.current_user_saved_shows_delete(shows=[item.id])


class SavedAlbums(ItemCollection, Mutable):
    """
    Class for managing the current user's saved ablums
    """

    def __init__(self, sp: Spotify):
        self.sp: Spotify = sp

    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Album]:
        raw_albums = self._items(
            self.sp.current_user_saved_albums,
            limit=limit,
            offset=offset,
            retrieve_all=retrieve_all,
        )
        if raw_albums is None:
            return None

        albums = []
        for album in raw_albums:
            album = album["album"]
            albums.append(Album(self.sp, album["id"], album))
        return albums

    def add(self, item: Album, **kwargs):
        self.sp.current_user_saved_albums_add(albums=[item.id])

    def remove(self, item: Album, **kwargs):
        self.sp.current_user_saved_albums_delete(albums=[item.id])

    def contains(self, item: Album):
        return self.sp.current_user_saved_albums_contains(albums=[item.id])[0]


class FollowedPlaylists(ItemCollection, Mutable):
    """
    Class for managing the current user's followed playlists
    """

    def __init__(self, sp: Spotify):
        self.sp: Spotify = sp

    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Playlist]:
        raw_playlists = self._items(
            self.sp.current_user_playlists,
            limit=limit,
            offset=offset,
            retrieve_all=retrieve_all,
        )
        if raw_playlists is None:
            return None

        playlists = []
        for playlist in raw_playlists:
            playlists.append(Playlist(self.sp, playlist["id"], info=playlist))
        return playlists

    def add(self, item: Playlist, **kwargs):
        self.sp.current_user_follow_playlist(playlist_id=item.id)

    def remove(self, item: Playlist, **kwargs):
        self.sp.current_user_unfollow_playlist(playlist_id=item.id)

    def contains(self, item: Playlist):
        return self.sp.playlist_is_following(item.id, [self.sp.me()["id"]])[0]


class FollowedArtists(ItemCollection, Mutable):
    """
    Class for managing the current user's followed artists
    """

    def __init__(self, sp: Spotify):
        self.sp: Spotify = sp

    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Artist]:
        # Wrap 'current_user_followed_artists' because the return format is different
        # from all other current user followed/saved get functions, for some reason.
        def wrapped_cur_followed_artists(*args, **kwargs):
            if "offset" in kwargs:
                kwargs.pop("offset")
            res = self.sp.current_user_followed_artists(*args, **kwargs)
            if res is None:
                return None
            return res["artists"]

        raw_artists = self._items(
            wrapped_cur_followed_artists,
            limit=limit,
            offset=offset,
            retrieve_all=retrieve_all,
        )
        if raw_artists is None:
            return None

        artists = []
        for artist in raw_artists:
            artists.append(Artist(self.sp, artist["id"], artist))
        return artists

    def add(self, item: Artist, **kwargs):
        self.sp.user_follow_artists([item.id])

    def remove(self, item: Artist, **kwargs):
        self.sp.user_unfollow_artists([item.id])

    def contains(self, item: Artist):
        return self.sp.current_user_following_artists([item.id])[0]
