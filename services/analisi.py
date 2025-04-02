from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.express as px
import pandas as pd
from collections import Counter

app = Flask(__name__)

# Configura Spotipy senza autenticazione utente
client_credentials_manager = SpotifyClientCredentials(client_id='YOUR_SPOTIFY_CLIENT_ID', client_secret='YOUR_SPOTIFY_CLIENT_SECRET')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_tracks_from_playlist(playlist_id):
    """Recupera i brani da una playlist."""
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        track_info = {
            'name': track['name'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'image_url': track['album']['images'][0]['url'],
            'spotify_url': track['external_urls']['spotify']
        }
        tracks.append(track_info)
    return tracks

def genera_grafici(tracks):
    """Genera i grafici per i top 5 artisti e album presenti nella playlist."""
    artisti = [artist for track in tracks for artist in track['artists'].split(', ')]
    album = [track['album'] for track in tracks]
    
    top_artisti = Counter(artisti).most_common(5)
    top_album = Counter(album).most_common(5)
    
    df_artisti = pd.DataFrame(top_artisti, columns=['Artista', 'Conteggio'])
    df_album = pd.DataFrame(top_album, columns=['Album', 'Conteggio'])
    
    fig_artisti = px.bar(df_artisti, x='Artista', y='Conteggio', title='Top 5 Artisti nella Playlist', color='Artista')
    fig_album = px.pie(df_album, names='Album', values='Conteggio', title='Top 5 Album nella Playlist')
    
    return fig_artisti.to_html(full_html=False), fig_album.to_html(full_html=False)

@app.route('/grafici_playlist')
def grafici_playlist():
    """Endpoint per ottenere i grafici della playlist."""
    playlist_id = request.args.get('playlist_id')
    if not playlist_id:
        return jsonify({'error': 'Playlist ID mancante'}), 400
    
    tracks = get_tracks_from_playlist(playlist_id)  # Recupera i brani della playlist
    if not tracks:
        return jsonify({'error': 'Nessun brano trovato'}), 404
    
    fig_artisti, fig_album = genera_grafici(tracks)
    return jsonify({'grafico_artisti': fig_artisti, 'grafico_album': fig_album})

if __name__ == "__main__":
    app.run(debug=True)
