from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from services.model import db, Playlist, Track  # Assicurati di avere Track nel tuo modello
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
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return []

@suggest_bp.route('/suggest', methods=['GET', 'POST'])
@login_required
def suggest_tracks():
    # Recupera le playlist dell'utente
    user_playlists = Playlist.query.filter_by(user_id=current_user.id).all()

    recommendations = []
    seed_type = None

    if request.method == 'POST':
        artist_name = request.form.get('artist_name')
        track_name = request.form.get('track_name')
        genre = request.form.get('genre')

        recommendations = get_suggestions(artist_name, track_name, genre)
        seed_type = 'Artista' if artist_name else 'Brano' if track_name else 'Genere'

    return render_template('suggest.html', user_playlists=user_playlists, recommendations=recommendations, seed_type=seed_type)

@suggest_bp.route('/add_track_to_playlist', methods=['POST'])
@login_required
def add_track_to_playlist():
    try:
        track_id = request.form['track_id']
        playlist_id = request.form['playlist_option']
        new_playlist_name = request.form.get('new_playlist_name')

        # Se l'utente ha scelto di creare una nuova playlist
        if playlist_id == 'new':
            if not new_playlist_name:
                return jsonify({"error": "Nome playlist non valido"}), 400

            # Crea una nuova playlist
            new_playlist = Playlist(user_id=current_user.id, name=new_playlist_name)
            db.session.add(new_playlist)
            db.session.commit()
            playlist_id = new_playlist.id

        # Ottieni il brano e la playlist
        track = Track.query.get(track_id)
        playlist = Playlist.query.get(playlist_id)

        if playlist and track:
            playlist.tracks.append(track)
            db.session.commit()
            return jsonify({"message": "Brano aggiunto alla playlist con successo", "playlist_name": playlist.name})

        return jsonify({"error": "Errore nell'aggiunta del brano alla playlist"}), 400
    except Exception as e:
        print(f"Errore nel backend: {e}")
        return jsonify({"error": "Errore interno del server"}), 500
