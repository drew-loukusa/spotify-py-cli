import abc 

class Followable(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def get_followed_items(self):
        raise NotImplemented
    
    @abc.abstractmethod
    def follow(self):
        """Follow a followable item"""
        raise NotImplementedError

    @abc.abstractclassmethod
    def unfollow(self):
        """Unfollow a followable item"""
        raise NotImplementedError

class Saveable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def save(self):
        """Save a saveable item"""
        raise NotImplementedError

    @abc.abstractclassmethod
    def unsave(self):
        """Unsave a saveable item"""
        raise NotImplementedError
    
class Utils(metaclass=abc.ABCMeta):
    @abc.abstractmethod 
    def _get_item(self):
        """Retreive an item from spotify, return item info or None"""
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self) -> str:
        """Make item printable"""
        raise NotImplementedError