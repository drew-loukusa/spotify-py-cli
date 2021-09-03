from time import sleep
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

# import textwrap
# from spotify_utils import *
def follow():
    scope = "playlist-modify-private playlist-read-private playlist-read-collaborative playlist-modify-public user-read-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


    playlist_id = "5ABMzUESx7K7EyowE5kFCl"
    playlist_owner_id = "ukfmusic"
    res = sp.playlist_is_following(playlist_id, [sp.me()["id"]])
    if res[0]:
        pprint.pprint(res)
        print("User was following playlist, unfollowing...")
        sleep(1)
        sp.user_playlist_unfollow(sp.me()["id"], playlist_id)

    result = sp.current_user_follow_playlist(playlist_id=playlist_id)


    pprint.pprint(result)
    pprint.pprint(type(result))

def playback():

    scope = "user-read-playback-state,user-modify-playback-state"
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

    # Shows playing devices
    res = sp.devices()
    pprint(res)

    # Change track
    sp.start_playback(uris=['spotify:track:6gdLoMygLsgktydTQ71b15'])

    # Change volume
    sp.volume(100)
    sleep(2)
    sp.volume(50)
    sleep(2)
    sp.volume(100)

if __name__ == "__main__":
    playback()