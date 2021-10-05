from typing import List
from spotipy import Spotify


def get_playlist(
    sp: Spotify, pl_name: str = None, pl_id: str = None
) -> List[dict]:
    """
    Attempts to retrieve a given playlist that the user is following.
    Accepts playlist name or id as ways of getting the playlist.
    Returns None if playlist is not being followed by the user

    Returns a list of dicts if the playlist exists (or multiple with the
    same name do).
    """
    playlists = sp.user_playlists(sp.me()["id"])
    selected_playlists = []
    for playlist in playlists["items"]:
        name, cur_id = playlist["name"], playlist["id"]
        if (
            pl_name is not None and name.strip() == pl_name.strip()
        ) or pl_id == cur_id:
            selected_playlists.append(playlist)

    return None if len(selected_playlists) == 0 else selected_playlists


def unfollow_all_pl(sp: Spotify, pl_name: str) -> None:
    """Attempts to unfollow all playlists with the same name"""
    playlists = get_playlist(sp, pl_name=pl_name)
    if playlists is not None:
        for playlist in playlists:
            pl_id, pl_name = playlist["id"], playlist["name"]
            sp.current_user_unfollow_playlist(playlist_id=pl_id)


def check_exists(sp: Spotify, pl_id: str) -> bool:
    """Checks if a playlist exists."""
    playlist = get_playlist(sp, pl_name=None, pl_id=pl_id)
    return playlist is not None


def get_pl_id(sp: Spotify, pl_name: str) -> List[str]:
    """
    Gets the id of a playlist(s) given a name.
    Returns None if playlist does not exist.

    Returns list of id strings if 1 or more playlists exist with given name.
    """
    id_list = []
    playlists = get_playlist(sp, pl_name=pl_name)
    if playlists is not None:
        for pl_list in playlists:
            id_list.append(pl_list["id"])
        return id_list
    return None
