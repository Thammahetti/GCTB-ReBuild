import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "4a2cbb97c5504b7dbe7a2efc0c840bf2"
SPOTIFY_CLIENT_SECRET = "0fb3aa1797704da5925b662d34732f95"
SPOTIFY_REDIRECT_URI = "https://5000-thammahetti-gctbrebuild-ih98jq29nrp.ws-eu117.gitpod.io/callback" 

sp_oauth = SpotifyOAuth(
client_id=SPOTIFY_CLIENT_ID,
client_secret=SPOTIFY_CLIENT_SECRET,
redirect_uri=SPOTIFY_REDIRECT_URI,
scope="user-read-private",
show_dialog=True 
)

def get_spotify_object(token_info):
    return spotipy.Spotify( auth=token_info['access_token'])