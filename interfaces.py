"""
This module contains interfaces and an abstract base class.
"""
from abc import ABCMeta, abstractmethod, abstractstaticmethod

from spotipy import Spotify

# Abstract base class
class Item(metaclass=ABCMeta):
    """
    Item should be inherited by all items (Playlist, Artist, Album, Track, Episode, Show, etc),
    and the items implement different interfaces as needed
    """

    def __init__(self, item_id: str, sp: Spotify, info: dict, name: str):
        self.id = item_id
        self.sp = sp
        self.info = info
        self.name = name
        self.msg = ""

    @abstractmethod
    def __repr__(self) -> str:
        """Make item printable"""
        raise NotImplementedError

    @abstractmethod
    def _get_item(self):
        """Retreive an item from spotify, return item info or None"""
        raise NotImplementedError


# Interface
class IFollowable(metaclass=ABCMeta):
    @abstractmethod
    def follow(self):
        """Follow a followable item"""
        raise NotImplementedError

    @abstractmethod
    def unfollow(self):
        """Unfollow a followable item"""
        raise NotImplementedError

    @abstractstaticmethod
    def get_followed_items(self):
        """Get all of a users followable items"""
        raise NotImplementedError


# Interface
class ISaveable(metaclass=ABCMeta):
    @abstractmethod
    def save(self):
        """Save a saveable item"""
        raise NotImplementedError

    @abstractmethod
    def unsave(self):
        """Unsave a saveable item"""
        raise NotImplementedError
