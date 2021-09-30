"""
This module contains item classes used for managing Spotify items.
"""

import textwrap

from typing import Collection, List
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
        super().__init__(
            sp, sp.track, item_id=item_id, item_type="track", info=info
        )

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

    def items(self, limit=20, offset=0, retrieve_all=False):
        raw_episodes = self._items(
            self.sp.show_episodes,
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

    def contains(self, item: Item):
        for ep in self.items(retrieve_all=True):
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
    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Track]:
        raw_tracks = self._items(
            self.sp.playlist_tracks,
            playlist_id=self.id,
            limit=limit,
            offset=offset,
            retrieve_all=retrieve_all,
        )
        if raw_tracks is None:
            return None

        tracks = []
        for track in raw_tracks:
            # TODO: Playlists can have episodes in them, add support for that
            tr = track["track"]
            tracks.append(Track(self.sp, tr["id"], tr))
        return tracks

    def contains(self, item: Item):
        for track in self.items(retrieve_all=True):
            if track.id == item.id:
                return True
        else:
            return False

    def change_details(
        self, name=None, public=None, collaborative=None, description=None
    ):
        self.sp.playlist_change_details(
            self.id,
            name=name,
            public=public,
            collaborative=collaborative,
            description=description,
        )

    def add(self, item: Item, **kwargs):
        """
        Add an item to the playlist.
        Item can be track or episode.
        Optional, uses keyword arg 'position' to determine where to place added item.
        If "position" is not given as a kwarg, default behavior is to add to the END of the playlist.
        """
        position = None if "position" not in kwargs else kwargs["position"]
        self.sp.playlist_add_items(self.id, [item.id], position=position)

    def remove(self, item: Item, **kwargs):
        """
        Remove an item from the playlist.
        Item can be track or episode.
        Optional:
        * Keyword arg 'positions'= [int, int, int...], a list of ints, determines which occurance of the item to remove .
        * Keyword arg 'all'=True, will cause ALL occurances of a specific item to be removed
        """
        config = lambda key, default: default if key not in kwargs else kwargs[key]
        positions = config("positions", None)
        remove_all = config("all", None)
        count = config("count", 1)
        offset = config("offset", (0, None))

        # TODO: Add THIRD mode of removal: 
        #       Walk through list, remove FIRST OCCURANCE and up to N occurances
        #       Basically, add kwarg support for the shit in remove in the cli
        #       Default behavior of just passing item ID should remove the FIRST instance of said item


        if remove_all:
            self.sp.playlist_remove_all_occurrences_of_items(self.id, [item.id])
        elif positions is not None:
            items = [{"uri": item.id, "positions": positions}]
            self.sp.playlist_remove_specific_occurrences_of_items(
                self.id, items
            )
        else:
            items = self.items(retrieve_all=True)
            start, end = offset
            end = end if end not in {-1, None} else len(items)
            for index, cur_item in enumerate(items[start:end]):
                if count == 0: 
                    break 
                if item.id == cur_item.id:
                    items = [{"uri": item.id, "positions": [index + start]}]
                    self.sp.playlist_remove_specific_occurrences_of_items(
                        self.id, items
                    )
                    count -= 1
            


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

    def items(self, limit=20, offset=0, retrieve_all=False):
        raw_tracks = self._items(
            self.sp.album_tracks,
            album_id=self.id,
            limit=limit,
            offset=offset,
            retrieve_all=retrieve_all,
        )
        if raw_tracks is None:
            return None
        tracks = []
        for track in raw_tracks:
            tr = track["track"]
            tracks.append(Track(self.sp, tr["id"], tr))
        return tracks

    def contains(self, item: Item):
        for track in self.items(retrieve_all=True):
            if track.id == item.id:
                return True
        else:
            return False
