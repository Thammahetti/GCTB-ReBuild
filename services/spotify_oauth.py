import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "8ef11c0c17b949c2b918993d3333d6b6"
SPOTIFY_CLIENT_SECRET = "754519f617294427bbc65f7a5e078e5f"
SPOTIFY_REDIRECT_URI = "https://studious-fortnight-v66v4vq464r92x5xr-5000.app.github.dev/callback" 

sp_oauth = SpotifyOAuth(
client_id=SPOTIFY_CLIENT_ID,
client_secret=SPOTIFY_CLIENT_SECRET,
redirect_uri=SPOTIFY_REDIRECT_URI,
scope="user-read-private",
show_dialog=True 
)

def get_spotify_object(token_info):
    return spotipy.Spotify( auth=token_info['access_token'])