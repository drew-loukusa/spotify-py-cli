"""
This module contains item classes used for managing Spotify items.
"""

import textwrap
from itertools import zip_longest

from typing import Collection, Counter, List
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
        name = self.info["name"]
        show = self.info["show"]["name"]
        description = textwrap.shorten(self.info["description"], width=500)
        rel_date = self.info["release_date"]
        url = self.info["external_urls"]["spotify"]
        item_id = self.info["id"]
        return f"Episode Name: {name}\nShow: {show}\nDescription: {description}\nRelease Date: {rel_date}\nURL: {url}\nID: {item_id}"


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
        name = self.info["name"]
        tr_id = self.info["id"]
        album = self.info["album"]["name"]
        artists = [item["name"] for item in self.info["artists"]]
        url = self.info["external_urls"]["spotify"]
        return f"Track Name: {name}\nAlbum: {album}\nArtist(s): {artists}\nURL: {url}\nID: {tr_id}"


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
        name = self.info["name"]
        publisher = self.info["publisher"]
        description = self.info["description"].rstrip()
        episode_count = self.info["total_episodes"]
        url = self.info["external_urls"]["spotify"]
        item_id = self.info["id"]
        return f"Show Name: {name}\nPublisher: {publisher}\nDescription: {description}\nEpisode Count: {episode_count}\nURL: {url}\nID: {item_id}"

    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Episode]:
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

    def remove(self, items: List[Item], **kwargs):
        """
        Remove an item from the playlist.
        Item can be track or episode.
        Optional:
        * Keyword arg 'positions'= [int, int, int...], a list of ints, determines which occurance of the item to remove .
        * Keyword arg 'all'=True, will cause ALL occurances of a specific item to be removed
        """
        config = (
            lambda key, default: default if key not in kwargs else kwargs[key]
        )
        positions = config("positions", None)
        remove_all = config("all", None)
        count = config("count", 1)
        offset = config("offset", (0, None))

        # TODO: Add THIRD mode of removal:
        #       Walk through list, remove FIRST OCCURANCE and up to N occurances
        #       Basically, add kwarg support for the shit in remove in the cli
        #       Default behavior of just passing item ID should remove the FIRST instance of said item
        item_ids = [item.id for item in items]

        if remove_all:
            self.sp.playlist_remove_all_occurrences_of_items(self.id, item_ids)

        specfic_items = []
        normal_items = dict()

        # Associate positions lists, if specified, to track ids
        for item, position_list in zip_longest(
            items, positions, fillvalue=None
        ):

            # Pos lit can be None, or can be empty if a track was skipped with '...'
            if position_list is not None and len(position_list) > 0:
                specfic_items.append(
                    {"uri": item.id, "positions": position_list}
                )
            else:
                normal_items[item.id] = count

        # Make inital call to handle specific positon specified tracks
        if len(specfic_items) > 0:
            self.sp.playlist_remove_specific_occurrences_of_items(
                self.id, specfic_items
            )

        # Then locate and remove tracks that did not have specific position lists
        # This is also how tracks are normally handeled when a user does not provide a list of position lists
        items = self.items(retrieve_all=True)
        start, end = offset
        end = end if end not in {-1, None} else len(items)
        target_items = []

        # Walk the playlist from 'start' to 'end'
        for index, cur_item in enumerate(items[start:end]):
            if count == 0:
                break

            # Check each item to see if it's one we want to remove
            if cur_item.id in normal_items:
                # If we've already "removed" 'count' occurances of said item, skip this occurance
                if normal_items[cur_item.id] <= 0:
                    continue
                target_items.append(
                    {"uri": cur_item.id, "positions": [index + start]}
                )
                normal_items[cur_item.id] -= 1

        self.sp.playlist_remove_specific_occurrences_of_items(
            self.id, target_items
        )


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

    def __str__(self) -> str:
        name = self.info["name"]
        rel_date = self.info["release_date"]
        artists = ", ".join([item["name"] for item in self.info["artists"]])
        track_count = self.info["total_tracks"]
        url = self.info["external_urls"]["spotify"]
        tr_id = self.info["id"]
        return f"Album Name: {name}\nArtist(s): {artists}\nRelease Date: {rel_date}\nURL: {url}\nTrack Count: {track_count}\nID: {tr_id}"

    def items(self, limit=20, offset=0, retrieve_all=False) -> List[Track]:
        raw_tracks = self._get_item(
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
