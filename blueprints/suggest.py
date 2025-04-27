from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required, current_user
from services.model import db, Playlist, Track, Playlist_suggested  # Import Playlist_suggested
import spotipy
from services.spotify_oauth import sp_oauth

suggest_bp = Blueprint('suggest_bp', __name__)

# Inizializzazione senza login usando le credenziali client
senza_login = spotipy.Spotify(client_credentials_manager=sp_oauth)

# Funzione per ottenere suggerimenti basati su un artista, brano o genere
def get_suggestions(artist_name=None, track_name=None, genre=None):
    try:
        suggestions = []
        # Ricerca per artista
        if artist_name:
            results = senza_login.search(q=f"artist:{artist_name}", type="artist", limit=1)
            if results['artists']['items']:
                artist = results['artists']['items'][0]
                artist_id = artist['id']
                # Restituire i brani di questo artista
                tracks = senza_login.artist_top_tracks(artist_id)
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

        # Ricerca per brano
        elif track_name:
            results = senza_login.search(q=f"track:{track_name}", type="track", limit=5)
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

        # Ricerca per genere
        elif genre:
            results = senza_login.search(q=f"genre:{genre}", type="track", limit=5)
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

        # Aggiungi le tracce suggerite alla tabella Playlist_suggested
        for track in recommendations:
            existing_track = Playlist_suggested.query.filter_by(name=track['name'], user_id=current_user.id).first()
            if not existing_track:
                new_suggestion = Playlist_suggested(
                    name=track['name'],
                    user_id=current_user.id
                )
                db.session.add(new_suggestion)
                db.session.commit()

    return render_template('suggest.html', user_playlists=user_playlists, recommendations=recommendations, seed_type=seed_type)

@suggest_bp.route('/add_track_to_playlist', methods=['POST'])
@login_required
def add_track_to_playlist():
    track_id = request.form.get('track_id')
    playlist_id = request.form.get('playlist_option')
    new_playlist_name = request.form.get('new_playlist_name')
    
    if track_id and playlist_id:
        # Ottieni il brano da Spotify API usando l'ID del brano
        track = senza_login.track(track_id)  # Ottieni i dettagli del brano tramite l'API Spotify
        
        if not track:
            return jsonify({'error': 'Brano non trovato su Spotify'}), 400
        
        # Verifica se la playlist esiste nel database
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist non trovata'}), 400

        # Aggiungi il brano alla playlist
        new_track = Track(
            name=track['name'],
            artist=track['artists'][0]['name'],
            image=track['album']['images'][0]['url'],
            external_url=track['external_urls']['spotify'],
            playlist_id=playlist.id
        )
        db.session.add(new_track)
        db.session.commit()

        # Modifica il nome della playlist
        playlist_name = playlist.title if hasattr(playlist, 'title') else 'Nome sconosciuto'
        return jsonify({'message': f'Brano {track["name"]} aggiunto con successo alla playlist {playlist_name}'}), 200

    return jsonify({'error': 'Dati mancanti'}), 400

@suggest_bp.route('/playlists')
@login_required  # Ensure the user is logged in
def playlists():
    # Get playlists for the current user from the database
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('playlists.html', playlists=playlists)
