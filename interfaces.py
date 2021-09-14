"""
This module contains interfaces and an abstract base class.
"""
from abc import ABCMeta, abstractmethod

from spotipy import Spotify, SpotifyException
import spotipy

# Abstract base class
class Item(metaclass=ABCMeta):
    """
    Item should be inherited by all items (Playlist, Artist, Album, Track, Episode, Show, etc)
    """

    def __init__(self, sp: Spotify, item_id: str, info: dict, name: str):
        self.sp = sp
        self.id = item_id
        self.info = info
        self.name = name
        self.msg = ""

    @abstractmethod
    def __repr__(self) -> str:
        """Make item printable"""
        raise NotImplementedError

    # Concrete classes should invoke this in their init methods
    @staticmethod
    def _get_item(concrete_getter, item_id):
        try:
            return concrete_getter(item_id)
        except SpotifyException as e:
            if e.http_status != 404:
                raise e
            else:
                return None


# Interface
class ItemCollection(metaclass=ABCMeta):
    def __init__(self, sp: Spotify):
        self.sp = sp

    @abstractmethod
    def add(self, item: Item):
        """Add an item to the collection"""
        raise NotImplementedError

    @abstractmethod
    def remove(self, item: Item):
        """Remove an item from the collection"""
        raise NotImplementedError

    @abstractmethod
    def contains(self, item: Item):
        """Check if item is a member of the collection"""
        raise NotImplementedError

    @abstractmethod
    def get_items(self):
        """Get a list of the items in the collection"""
        raise NotImplementedError
