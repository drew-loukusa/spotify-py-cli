"""
This module contains item classes used for managing Spotify items.
"""

import textwrap

from typing import List
from spotipy import Spotify

from interfaces import Item, ItemCollection, Mutable


class Episode(Item):
    """
    Class for holding info related to a single Spotify Episode
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        super().__init__(
            sp, sp.episode, item_id=item_id, item_type="episode", info=info
        )

    def __repr__(self) -> str:
        return f"<Episode: name: {self.name}, id: {self.id}>"

    def __str__(self) -> str:
        return f"<Episode: name: {self.name}, id: {self.id}>"


class Track(Item):
    """
    Class for holding info related to a single Spotify Track
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        if info is None:
            info = Item._get_item(sp.episode, item_id)
        name = info["name"]
        super().__init__(item_id, sp, info, name, item_type="track")

    def __repr__(self) -> str:
        return f"<Track: name: {self.name}, id: {self.id}>"

    def __str__(self) -> str:
        return f"<Track: name: {self.name}, id: {self.id}>"


class Show(Item, ItemCollection):
    """
    Class for holding info related to a single Spotify Show
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        super().__init__(
            sp, sp.show, item_id=item_id, item_type="show", info=info
        )

    def __repr__(self) -> str:
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    def __str__(self):
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    @property
    def items(self):
        raw_episodes = self._items(self.sp.show_episodes)
        if raw_episodes is None:
            return None
        episodes = []
        for episode in raw_episodes:
            ep = episode["episode"]
            episodes.append(Episode(self.sp, ep["id"], ep))
        return episodes

    def contains(self, item: Item):
        for ep in self.items:
            if item.id == ep.id:
                return True
        return False


class Playlist(Item, ItemCollection, Mutable):
    """
    Class for holding info related to a single Spotify Playlist
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        super().__init__(
            sp, sp.playlist, item_id=item_id, item_type="playlist", info=info
        )

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
        raw_tracks = self._items(self.sp.playlist_tracks, playlist_id=self.id)
        if raw_tracks is None:
            return None

        tracks = []
        for track in raw_tracks:
            # TODO: Playlists can have episodes in them, add support for that
            tr = track["track"]
            tracks.append(Track(self.sp, tr["id"], tr))
        return tracks

    def contains(self, item: Item):
        for track in self.items:
            if track.id == item.id:
                return True
        else:
            return False

    def add(self, item: Item):
        "item can be track or episode"
        self.sp.playlist_add_items(self.id, [item.id])

    def remove(self, item: Item):
        self.sp.playlist_remove_all_occurrences_of_items(self.id, [item.id])


class Artist(Item):
    """
    Class for holding info related to a single Spotify Artist
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        super().__init__(sp, sp.artist, item_id, item_type="artist", info=info)

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


class Album(Item, ItemCollection):
    """
    Class for holding info related to a single Spotify Album
    """

    def __init__(self, sp: Spotify, item_id: str, info=None):
        super().__init__(
            sp, sp.album, item_id=item_id, item_type="album", info=info
        )

    def __repr__(self) -> str:
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    def __str__(self):
        return f"<{self.type}: name: {self.name}, id: {self.id}>"

    @property
    def items(self) -> List[Item]:
        raw_tracks = self._get_item(self.sp.album_tracks, self.id)
        if raw_tracks is None:
            return None
        tracks = []
        for track in raw_tracks:
            tr = track["track"]
            tracks.append(Track(self.sp, tr["id"], tr))
        return tracks

    def contains(self, item: Item):
        for track in self.items:
            if track.id == item.id:
                return True
        else:
            return False
