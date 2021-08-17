import spotipy
import pprint
import textwrap
from spotify_utils import *
from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-modify-private playlist-read-private playlist-read-collaborative playlist-modify-public user-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


playlist_id = "5ABMzUESx7K7EyowE5kFCl"
playlist_owner_id = "ukfmusic"
result = sp.user_playlist_follow_playlist(playlist_owner_id, playlist_id)
result = sp.user_playlist_is_following(playlist_owner_id, playlist_id, [sp.me()["id"]])

pprint.pprint(result)
