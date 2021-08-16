import spotipy
import pprint
import textwrap
from spotify_utils import *
from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-modify-private playlist-read-private playlist-read-collaborative playlist-modify-public user-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

q = "Massive Drum & Bass"
q.replace(" ", "+")
result = sp.search(q, limit=10, offset=0, type="playlist", market=None)

# pprint.pprint(result['playlists']['items']

for playlist in result["playlists"]["items"]:
    print("-----------------------")
    print(f"Name:\t\t{playlist['name']}")

    desc = playlist["description"]
    wrapped_desc = textwrap.wrap(
        "Description:\t" + desc,
        width=64,
        initial_indent="",
        subsequent_indent="\t\t",
    )
    for line in wrapped_desc:
        print(line)

    print(f"Owner:\t\t{playlist['owner']['display_name']}")
    print(f"Track count:\t{playlist['tracks']['total']}")

    print(f"Playlist id:\t{playlist['id']}")
    print(f"Owner id:\t{playlist['owner']['id']}")
