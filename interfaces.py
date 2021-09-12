"""
This module contains interfaces and an abstract base class.
"""
import abc

import spotipy

# Abstract base class
class Item(metaclass=abc.ABCMeta):
    """
    Item inherited by all items (Playlist, Artist, Album, Track, Episode, Show, etc),
    and the items implement different interfaces as needed
    """

    def __init__(
        self, item_id: str, sp: spotipy.Spotify, info: dict, name: str
    ):
        self.id = item_id
        self.sp = sp
        self.info = info
        self.name = name
        self.msg = ""

    @abc.abstractmethod
    def __repr__(self) -> str:
        """Make item printable"""
        raise NotImplementedError

    @abc.abstractmethod
    def _get_item(self):
        """Retreive an item from spotify, return item info or None"""
        raise NotImplementedError


# Interface
class IFollowable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def follow(self):
        """Follow a followable item"""
        raise NotImplementedError

    @abc.abstractclassmethod
    def unfollow(self):
        """Unfollow a followable item"""
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def get_followed_items(self):
        """Get all of a users followable items"""
        raise NotImplementedError


# Interface
class ISaveable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def save(self):
        """Save a saveable item"""
        raise NotImplementedError

    @abc.abstractclassmethod
    def unsave(self):
        """Unsave a saveable item"""
        raise NotImplementedError
