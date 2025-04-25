from flask import Blueprint, request, render_template
import spotipy
from services.spotify_oauth import sp_oauth

suggest_bp = Blueprint('suggest', __name__)

# Gestione senza login
senza_login = spotipy.Spotify(client_credentials_manager=sp_oauth)

# Funzione per ottenere suggerimenti basati su un artista, brano o genere
def get_suggestions(artist_name=None, track_name=None, genre=None):
    try:
        # Ricerca per artista
        if artist_name:
            results = senza_login.search(q=f"artist:{artist_name}", type="artist", limit=1)
            if results['artists']['items']:
                artist = results['artists']['items'][0]
                artist_id = artist['id']
                # Restituire i brani di questo artista
                tracks = senza_login.artist_top_tracks(artist_id)
                suggestions = []
                for track in tracks['tracks']:
                    suggestion = {
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'image': track['album']['images'][0]['url'],
                        'preview_url': track.get('preview_url', None),
                        'external_url': track['external_urls']['spotify'],
                        'id': track['id']
                    }
                    suggestions.append(suggestion)
                return suggestions

        # Ricerca per brano
        elif track_name:
            results = senza_login.search(q=f"track:{track_name}", type="track", limit=5)
            suggestions = []
            for track in results['tracks']['items']:
                suggestion = {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'image': track['album']['images'][0]['url'],
                    'preview_url': track.get('preview_url', None),
                    'external_url': track['external_urls']['spotify'],
                    'id': track['id']
                }
                suggestions.append(suggestion)
            return suggestions

        # Ricerca per genere
        elif genre:
            results = senza_login.search(q=f"genre:{genre}", type="track", limit=5)
            suggestions = []
            for track in results['tracks']['items']:
                suggestion = {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'image': track['album']['images'][0]['url'],
                    'preview_url': track.get('preview_url', None),
                    'external_url': track['external_urls']['spotify'],
                    'id': track['id']
                }
                suggestions.append(suggestion)
            return suggestions
        
        return []
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return []

@suggest_bp.route('/suggest', methods=['GET', 'POST'])
def suggest_tracks():
    if request.method == 'POST':
        artist_name = request.form.get('artist_name')
        track_name = request.form.get('track_name')
        genre = request.form.get('genre')

        recommendations = get_suggestions(artist_name, track_name, genre)
        seed_type = 'Artista' if artist_name else 'Brano' if track_name else 'Genere'

        return render_template('suggest.html', recommendations=recommendations, seed_type=seed_type)

    return render_template('suggest.html', recommendations=None, seed_type=None)
