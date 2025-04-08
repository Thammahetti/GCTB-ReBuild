import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import plotly.express as px
from collections import Counter

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
            'spotify_url': track['external_urls']['spotify'],
            'popularity': track['popularity'],
            'duration_ms': track['duration_ms'],
            'release_date': track['album']['release_date'],
        }
        tracks.append(track_info)
    return tracks

def generare_grafico_temporale(tracks):
    """Genera un grafico che mostra il numero di brani pubblicati per anno."""
    release_years = [track['release_date'][:4] for track in tracks]
    release_years_counter = Counter(release_years).most_common()
    df_release_years = pd.DataFrame(release_years_counter, columns=['Anno', 'Conteggio'])
    fig_release_years = px.bar(df_release_years, x='Anno', y='Conteggio', title='Distribuzione Temporale dei Brani')
    return fig_release_years

def generare_grafico_durata(tracks):
    """Genera un grafico che mostra la distribuzione della durata dei brani."""
    durations = [track['duration_ms'] / 1000 / 60 for track in tracks]  # durata in minuti
    fig_durations = px.histogram(durations, nbins=20, title='Distribuzione della Durata dei Brani (minuti)')
    return fig_durations

def generare_grafico_popolarita(tracks):
    """Genera un grafico che mostra la distribuzione della popolarità dei brani."""
    popularity = [track['popularity'] for track in tracks]
    fig_popularity = px.histogram(popularity, nbins=10, title='Distribuzione della Popolarità dei Brani')
    return fig_popularity

def generare_grafico_generi(tracks):
    """Genera un grafico dei generi musicali nella playlist."""
    generi = [track['artists'] for track in tracks]
    if not generi:
        return "Nessun dato sui generi disponibili."

    artisti = [artist for track in tracks for artist in track['artists'].split(', ')]
    artisti_counter = Counter(artisti).most_common(10)
    df_artisti = pd.DataFrame(artisti_counter, columns=['Artista', 'Conteggio'])
    fig_artisti = px.bar(df_artisti, x='Artista', y='Conteggio', title='Top 10 Artisti nella Playlist')
    return fig_artisti

def generare_evoluzione_popolarita(tracks):
    """Genera un grafico a linee che mostra l'evoluzione della popolarità nel tempo."""
    years = [track['release_date'][:4] for track in tracks]
    popularity = [track['popularity'] for track in tracks]
    
    df = pd.DataFrame({'Anno': years, 'Popolarità': popularity})
    df_grouped = df.groupby('Anno').mean().reset_index()

    fig_popularity_over_time = px.line(df_grouped, x='Anno', y='Popolarità', title="Evoluzione della Popolarità nel Tempo")
    return fig_popularity_over_time
