import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "51732c4254124416b138a4114f3399f9"
SPOTIFY_CLIENT_SECRET = "71185d62c08749e6ab66a9e42507b90a"
SPOTIFY_REDIRECT_URI = "https://curly-invention-q77qrqpr7r5vcqpp-5000.app.github.dev/callback" 

sp_oauth = SpotifyOAuth(
client_id=SPOTIFY_CLIENT_ID,
client_secret=SPOTIFY_CLIENT_SECRET,
redirect_uri=SPOTIFY_REDIRECT_URI,
scope="user-read-private",
show_dialog=True 
)

def get_spotify_object(token_info):
    return spotipy.Spotify( auth=token_info['access_token'])