from time import sleep
import spotipy
import pprint
import textwrap
from spotify_utils import *
from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-modify-private playlist-read-private playlist-read-collaborative playlist-modify-public user-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


playlist_id = "5ABMzUESx7K7EyowE5kFCl"
playlist_owner_id = "ukfmusic"
if sp.playlist_is_following(playlist_id, [sp.me()["id"]])[0]:
    print("User was following playlist, unfollowing...")
    sleep(1)
    sp.user_playlist_unfollow(sp.me()["id"], playlist_id)

result = sp.current_user_follow_playlist(playlist_id=playlist_id)


pprint.pprint(result)
pprint.pprint(type(result))
