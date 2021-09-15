"""
This module contains interfaces and an abstract base class.
"""
from typing import List
from abc import ABCMeta, abstractmethod

from spotipy import Spotify, SpotifyException

# Abstract base class
class Item(metaclass=ABCMeta):
    """
    Item should be inherited by all items (Playlist, Artist, Album, Track, Episode, Show, etc)
    """

    def __init__(
        self,
        sp: Spotify,
        concrete_getter,
        item_id: str,
        item_type: str,
        info: dict,
    ):

        self.sp = sp
        self.id = item_id
        self.info = info

        if info is None:
            self.info = self._get_item(concrete_getter, item_id)

        self.name = None
        if self.info is not None:
            self.name = self.info["name"]

        self.type = item_type
        self.msg = ""

    @abstractmethod
    def __str__(self) -> str:
        """Make item printable"""
        raise NotImplementedError

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
    """
    A class should implement this interface if it can "hold" a collection of items.
    A class can be an Item, and an ItemCollection, example: Playlist or Album
    """

    @property
    @abstractmethod
    def items(self) -> List[Item]:
        """Get a list of the items in the collection"""
        raise NotImplementedError

    @abstractmethod
    def contains(self, item: Item):
        """Check if item is a member of the collection"""
        raise NotImplementedError


# Interface
class Mutable:
    """
    If an ItemCollection is mutable (modifiable, editable) by the user,
    said ItemCollection should implement this interface.
    """

    @abstractmethod
    def add(self, item: Item):
        """Add an item to the collection"""
        raise NotImplementedError

    @abstractmethod
    def remove(self, item: Item):
        """Remove an item from the collection"""
        raise NotImplementedError
