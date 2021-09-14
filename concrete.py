import textwrap
from spotipy import Spotify
from interfaces import Item, ItemCollection


class Playlist(Item):  # , ItemCollection
    def __init__(self, sp: Spotify, item_id: str, info=None):
        info = Item._get_item(sp.playlist, item_id) if info is None else info
        name = None if info is None else info["name"]
        super().__init__(sp, item_id, info, name, item_type="Playlist")

    def __repr__(self):
        return f"[{self.type}: {self.name}, {self.id}]"

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


class FollowedPlaylists(ItemCollection):
    def __init__(self, sp: Spotify):
        super().__init__(sp)

    def add(self, item: Playlist):
        self.sp.current_user_follow_playlist(playlist_id=item.id)

    def remove(self, item: Playlist):
        self.sp.current_user_unfollow_playlist(playlist_id=item.id)

    def contains(self, item: Playlist):
        return self.sp.playlist_is_following(item.id, [self.sp.me()["id"]])[0]

    @property
    def items(self):
        playlists = []
        res = self.sp.current_user_playlists()
        if res is None:
            return None
        for playlist in res["items"]:
            playlists.append(Playlist(self.sp, playlist["id"], info=playlist))
        return playlists


class Artist(Item):
    def __init__(self, sp: Spotify, item_id: str, info=None):
        info = sp.artist(item_id) if info is None else info
        name = None if info is None else info["name"]
        super().__init__(sp, item_id, info, name, item_type="Artist")

    def __repr__(self):
        return f"[{self.type}: {self.name}, {self.id}]"

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


class FollowedArtists(ItemCollection):
    def __init__(self, sp: Spotify):
        super().__init__(sp)

    def add(self, item: Artist):
        self.sp.user_follow_artists([item.id])

    def remove(self, item: Artist):
        self.sp.user_unfollow_artists([item.id])

    def contains(self, item: Artist):
        return self.sp.current_user_following_artists([item.id])[0]

    @property
    def items(self):
        artists = []
        res = self.sp.current_user_followed_artists()
        if res is None:
            return None

        for artist in res["artists"]["items"]:
            artists.append(Artist(self.sp, artist["id"], artist))
