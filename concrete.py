import textwrap
from typing import List
from spotipy import Spotify
from interfaces import Item, ItemCollection, Mutable


class Episode(Item):
    """
    TODO: Add doc string
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        info = Item._get_item(sp.episode, item_id) if info is None else info
        name = None if info is None else info["name"]
        super().__init__(item_id, sp, info, name, item_type="episode")

    def __repr__(self) -> str:
        return f"<Episode: name: {self.name}, id: {self.id}>"

    def __str__(self) -> str:
        return f"<Episode: name: {self.name}, id: {self.id}>"


class SavedEpisodes(ItemCollection, Mutable):
    """
    TODO: Add doc string
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


class Track(Item):
    """
    TODO: Add doc string
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        info = Item._get_item(sp.track, item_id) if info is None else info
        name = None if info is None else info["name"]
        super().__init__(item_id, sp, info, name, item_type="track")

    def __repr__(self) -> str:
        return f"<Track: name: {self.name}, id: {self.id}>"

    def __str__(self) -> str:
        return f"<Track: name: {self.name}, id: {self.id}>"


class SavedTracks(ItemCollection, Mutable):
    """
    TODO: Add doc string
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


class Show(Item, ItemCollection):
    """
    TODO: Add doc string
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        info = Item._get_item(sp.show, item_id) if info is None else info
        name = None if info is None else info["name"]
        super().__init__(sp, item_id, info, name, item_type="show")

    def __repr__(self) -> str:
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    def __str__(self):
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    @property
    def items(self):
        raise NotImplementedError
        # self.sp.show_episodes(self.id, limit=50)

    def contains(self, item: Item):
        raise NotImplementedError
        # There isn't a 'show_contains_episode' method,
        # so I will probably have to do it by hand


class SavedShows(ItemCollection, Mutable):
    """
    TODO: Add doc string
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


class Playlist(Item, ItemCollection, Mutable):
    """
    TODO: Add doc string
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        info = Item._get_item(sp.playlist, item_id) if info is None else info
        name = None if info is None else info["name"]
        super().__init__(sp, item_id, info, name, item_type="playlist")

    def __repr__(self):
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    def __str__(self):
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

    # Playlist implements ItemCollection since it "holds" a collection of tracks
    @property
    def items(self):
        raise NotImplementedError
        self.sp.playlist_tracks(self.id)

    def add(self, item: Item):
        "item can be track or episode"
        self.sp.playlist_add_items(self.id, [item.id])

    def remove(self, item: Item):
        self.sp.playlist_remove_all_occurrences_of_items(self.id, [item.id])

    def contains(self, item: Item):
        self.sp.current_user


class FollowedPlaylists(ItemCollection, Mutable):
    """
    TODO: Add doc string
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


class Artist(Item):
    """
    TODO: Add doc string
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        info = sp.artist(item_id) if info is None else info
        name = None if info is None else info["name"]
        super().__init__(sp, item_id, info, name, item_type="artist")

    def __repr__(self):
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    def __str__(self):
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


class FollowedArtists(ItemCollection, Mutable):
    """
    TODO: Add doc string
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


class Album(Item, ItemCollection):
    """
    TODO: Add doc string
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        info = Item._get_item(sp.album, item_id) if info is None else info
        name = None if info is None else info["name"]
        super().__init__(item_id, sp, info, name, item_type="album")

    def __repr__(self) -> str:
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    def __str__(self):
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    @property
    def items(self) -> List[Item]:
        raise NotImplementedError
        self.sp.album_tracks(self.id, limit=None)

    def contains(self, item: Item):
        raise NotImplementedError
        # Same as Show, album does not have a "album_contains_item" method
        # So you'll have to do this one by hand


class FollowedAlbums(ItemCollection, Mutable):
    """
    TODO: Add doc string
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
