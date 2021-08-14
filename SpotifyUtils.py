import spotipy
from typing import List


def search_public_playlist(sp, query, limit=10, market=None):
    """Search public playlists."""
    q = query.replace(" ", "+")
    results = sp.search(q, limit=limit, offset=0, type="playlist", market=None)
    if results != None:
        return results["playlists"]["items"]
    return None


def create_playlist(
    sp: spotipy.Spotify, name: str, public=False, collaborative=False, description=""
) -> str:
    """Attempts to create a playlist with the given name, returns the playlist id if successful"""

    # TODO: add support for
    # public - is the created playlist public
    # collaborative - is the created playlist collaborative
    # description - the description of the playlist

    user_id = sp.me()["id"]
    result = sp.user_playlist_create(
        user_id,
        name=name,
        public=public,
        collaborative=collaborative,
        description=description,
    )
    return result["id"]


def list_playlists(sp: spotipy.Spotify) -> None:
    user_id = sp.me()["id"]
    playlists = sp.user_playlists(user_id)
    for playlist in playlists["items"]:
        print(playlist["name"])


def delete_playlist(sp: spotipy.Spotify, pl_id: str) -> None:
    """Attempts to delete the playlist with the id 'pl_id'"""
    sp.current_user_unfollow_playlist(playlist_id=pl_id)


def delete_all(sp: spotipy.Spotify, pl_name: str) -> None:
    """Attempts to delete all playlists with the same name"""
    playlists = get_playlist(sp, pl_name=pl_name)
    if playlists is not None:
        for playlist in playlists:
            pl_id, pl_name = playlist["id"], playlist["name"]
            sp.current_user_unfollow_playlist(playlist_id=pl_id)


# I'd assume there is a better way to do this.
# However, how many users are going to have > 100 playlists?
# Not many. And even the outliers probably have < 1000 playlists.
# Search in a linear fashion through < 1000 vaules is easy for a computer.
# Might improve this at some point, but for now it's fine. TODO maybe.


def check_exists(sp: spotipy.Spotify, pl_id: str) -> bool:
    """Checks if a playlist exists."""
    playlist = get_playlist(sp, pl_name=None, pl_id=pl_id)
    return True if playlist != None else False


def get_pl_id(sp: spotipy.Spotify, pl_name: str) -> List[str]:
    """
    Gets the id of a playlist(s) given a name.
    Returns None if playlist does not exist.

    Returns list of id strings if 1 or more playlists exist with given name.
    """
    id_list = []
    playlists = get_playlist(sp, pl_name=pl_name)
    if playlists != None:
        for pl in playlists:
            id_list.append(pl["id"])
        return id_list
    return None


def get_playlist(
    sp: spotipy.Spotify, pl_name: str = None, pl_id: str = None
) -> List[dict]:
    """
    Attempts to retrieve all info related to a given playlist.
    Accepts playlist name or id as ways of getting the playlist.
    Returns None if playlists does not exit

    Returns a list of dicts if the playlist exists (or multiple with the
    same name do).
    """
    user_id = sp.me()["id"]
    playlists = sp.user_playlists(user_id)
    selected_playlists = []
    for playlist in playlists["items"]:
        name, id = playlist["name"], playlist["id"]
        if (pl_name != None and name.strip() == pl_name.strip()) or id == pl_id:
            selected_playlists.append(playlist)

    return None if len(selected_playlists) == 0 else selected_playlists
