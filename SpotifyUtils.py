import spotipy


def create_playlist(sp: spotipy.Spotify, name: str) -> str:
    """Attempts to create a playlist with the given name, returns the playlist id if successful"""
    user_id = sp.me()["id"]
    result = sp.user_playlist_create(user_id, name=name, public=False)
    return result["id"]


def list_playlists(sp: spotipy.Spotify) -> None:
    user_id = sp.me()["id"]
    playlists = sp.user_playlists(user_id)
    for playlist in playlists["items"]:
        print(playlist["name"])


def delete_playlist(sp: spotipy.Spotify, pl_id: str) -> None:
    """Attempts to delete the playlist with the id 'pl_id'"""
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


def get_pl_id(sp: spotipy.Spotify, pl_name: str) -> str:
    """
    Gets the id of a playlist given a name.
    Returns None if playlist does not exist.
    """
    playlist = get_playlist(sp, pl_name=pl_name)
    if playlist != None:
        return playlist["id"]
    return None


def get_playlist(sp: spotipy.Spotify, pl_name: str = None, pl_id: str = None) -> dict:
    """
    Attempts to retrieve all info related to a given playlist.
    Accepts playlist name or id as ways of getting the playlist.
    Returns None if playlists does not exit
    Returns a dict of info if it does exist
    """
    user_id = sp.me()["id"]
    playlists = sp.user_playlists(user_id)
    for playlist in playlists["items"]:
        name, id = playlist["name"], playlist["id"]
        if (pl_name != None and name.strip() == pl_name.strip()) or id == pl_id:
            return playlist

    return None
