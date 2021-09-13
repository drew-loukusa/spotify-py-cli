"""
This module contains interfaces and an abstract base class.
"""
from abc import ABCMeta, abstractmethod, abstractstaticmethod

from spotipy import Spotify, SpotifyException

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

    @abstractstaticmethod
    def get_item(sp: Spotify, item_id: str):
        """Retreive an item from spotify, return item info or None"""
        raise NotImplementedError

    # Concrete classes invoke this when defining an implementation of
    # 'get_item' and pass in their specific method for getting their
    # item info from the Spotify instance
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
class IFollowable(metaclass=ABCMeta):
    @abstractmethod
    def follow(self):
        """Follow a followable item"""
        raise NotImplementedError

    @abstractmethod
    def unfollow(self):
        """Unfollow a followable item"""
        raise NotImplementedError

    @abstractmethod
    def following(self):
        """Check if current user is following item"""
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
    def saved(self):
        """Checks if current user has item saved in library"""
        raise NotImplementedError

    @abstractmethod
    def unsave(self):
        """Unsave a saveable item"""
        raise NotImplementedError
