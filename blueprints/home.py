# home.py
from flask import Blueprint, redirect, request, url_for, session, render_template, jsonify
import spotipy
from services.spotify_oauth import sp_oauth, get_spotify_object
from spotipy.oauth2 import SpotifyClientCredentials
from services.model import db, Playlist, User
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

home_bp = Blueprint('home', __name__)


senza_login = spotipy.Spotify(client_credentials_manager=sp_oauth)

@home_bp.route('/home1')
def home1():
    token_info = session.get('spotify_token', None)
    if not token_info:
        return redirect(url_for('auth.logout_spotify'))  

    sp = get_spotify_object(token_info)
    user_info = sp.current_user()  
    playlists = sp.current_user_playlists()  
    playlists_info = playlists['items']

    return render_template('home.html', user_info=user_info, playlists=playlists_info)


@home_bp.route('/playlist/<playlist_id>')
def playlist_details(playlist_id):
    token_info = session.get('spotify_token', None)
    if not token_info:
        return redirect(url_for('auth.logout_spotify'))  

    sp = get_spotify_object(token_info)
    brani = sp.playlist_items(playlist_id)
    brani_specifici = brani['items']

    return render_template('brani.html', brani=brani_specifici)




@home_bp.route('/brani_playlist')
def brani_playlist():
    playlist_id = request.args.get('playlist_id')

    if playlist_id:
        try:
            # Recupera i brani della playlist
            playlist = senza_login.playlist_tracks(playlist_id)

            tracks = playlist.get('items', [])  # Prende la lista dei brani
            
            cleaned_tracks = []
            for track in tracks:
                track_info = track.get('track', {})  # Prendi il dizionario 'track'

                if not isinstance(track_info, dict):  # Controllo se è effettivamente un dizionario
                    continue
                
                track_name = track_info.get('name', 'Unknown Track')
                artist_names = ', '.join([artist.get('name', 'Unknown') for artist in track_info.get('artists', [])])
                album_name = track_info.get('album', {}).get('name', 'Unknown Album')

                # Controllo immagini album
                album_images = track_info.get('album', {}).get('images', [{'url': '/static/default-image.jpg'}])
                image_url = album_images[0]['url'] if album_images else '/static/default-image.jpg'

                cleaned_tracks.append({
                    'name': track_name,
                    'artists': artist_names,
                    'album': album_name,
                    'image_url': image_url,
                    'id': track_info.get('id', '')
                })

            return render_template('brani_playlist.html', tracks=cleaned_tracks, playlist_id=playlist_id)

        except Exception as e:
            return f"Errore durante il recupero dei brani: {str(e)}", 500

    return "Playlist ID not found", 404


@home_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')

    if query:
        # Search for playlists
        results = senza_login.search(q=query, type='playlist', limit=10)
        playlists = results.get('playlists', {}).get('items', [])

        cleaned_playlists = []

        for playlist in playlists:
            if playlist is None:
                continue

            playlist['images'] = playlist.get('images', [{'url': '/static/default-image.jpg'}])
            playlist['name'] = playlist.get('name', 'Unknown Playlist')
            playlist['owner'] = playlist.get('owner', {'display_name': 'Unknown'})

            cleaned_playlists.append(playlist)



        return render_template('index.html', playlists=cleaned_playlists, query=query)

    else:
        cleaned_playlists = []
        return render_template('index.html', playlists=cleaned_playlists, query=None)

@home_bp.route('/add_playlist', methods=['POST'])
def add_playlist():
    # Get the playlist ID from the request
    data = request.get_json()
    playlist_id = data.get('playlist_id')

    if not playlist_id:
        return jsonify({"success": False, "message": "Playlist ID is required"}), 400

    # Ensure the user is logged in (check session or other authentication)
    if not session.get('user_id'):
        return jsonify({"success": False, "message": "User not logged in"}), 401

    user_id = session.get('user_id')  # Get the user ID from the session (or wherever you're storing user data)

    # Check if the playlist already exists in the user's saved playlists
    existing_playlist = Playlist.query.filter_by(user_id=user_id, playlist_id=playlist_id).first()
    if existing_playlist:
        return jsonify({"success": False, "message": "Playlist already added"}), 400

    try:
        # Create a new Playlist record and save it to the database
        new_playlist = Playlist(user_id=user_id, playlist_id=playlist_id)
        db.session.add(new_playlist)
        db.session.commit()

        return jsonify({"success": True, "message": "Playlist added successfully!"})

    except Exception as e:
        # Handle any potential errors and return an error message
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Route to display the playlists the user has saved
@home_bp.route('/my_playlists')
def my_playlists():
    if not session.get('user_id'):
        return redirect(url_for('auth.logout_spotify'))

    user_id = session.get('user_id')
    playlists = Playlist.query.filter_by(user_id=user_id).all()

    if not playlists:
        return render_template('my_playlists.html', playlists=None, message="You haven't added any playlists yet.")

    sp = senza_login

    playlist_details = []

    for playlist in playlists:
        try:
            spotify_playlist = sp.playlist(playlist.playlist_id)
            playlist_details.append({
                'id': playlist.playlist_id, 
                'name': spotify_playlist['name'],
                'url': spotify_playlist['external_urls']['spotify'],
                'image_url': spotify_playlist['images'][0]['url'] if spotify_playlist['images'] else '/static/default-image.jpg'
            })
        except Exception as e:
            print(f"Error fetching playlist {playlist.playlist_id}: {e}")

    return render_template('my_playlists.html', playlists=playlist_details)


@home_bp.route('/compare_playlists')
def compare_playlists():
    playlist_ids = request.args.get('playlist_ids').split(',')

    if len(playlist_ids) != 2:
        return "Please select exactly two playlists for comparison.", 400

    # Fetch the tracks for both playlists
    tracks_playlist_1 = get_tracks_from_playlist(playlist_ids[0])
    tracks_playlist_2 = get_tracks_from_playlist(playlist_ids[1])

    # Find common tracks
    common_tracks = tracks_playlist_1.intersection(tracks_playlist_2)
    common_count = len(common_tracks)

    # Calculate similarity percentage
    total_tracks_1 = len(tracks_playlist_1)
    total_tracks_2 = len(tracks_playlist_2)
    similarity_percentage = (common_count / (min(total_tracks_1, total_tracks_2) + 0.1)) * 100

    # Fetch playlist details
    playlists = get_playlists_by_ids(playlist_ids)

    # Prepare data for the graph
    playlist_data = {
        'playlist_1': {
            'name': playlists[0]['name'],
            'total_tracks': total_tracks_1,
            'common_tracks': common_count,
            'similarity_percentage': similarity_percentage,
        },
        'playlist_2': {
            'name': playlists[1]['name'],
            'total_tracks': total_tracks_2,
            'common_tracks': common_count,
            'similarity_percentage': similarity_percentage,
        },
    }

    # Create the graph using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[playlists[0]['name'], playlists[1]['name']],
        y=[total_tracks_1, total_tracks_2],
        name='Total Tracks',
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=[playlists[0]['name'], playlists[1]['name']],
        y=[common_count, common_count],
        name='Common Tracks',
        marker_color='green'
    ))

    fig.update_layout(
        title="Track Comparison Between Playlists",
        xaxis_title="Playlist",
        yaxis_title="Number of Tracks",
        barmode="group",
        template="plotly_dark",
    )

    # Render the comparison page with the graph
    return render_template('compare_playlist.html', playlists=playlists, playlist_data=playlist_data, graph=fig.to_html())

def get_playlists_by_ids(playlist_ids):
    playlists = []
    
    # Make requests to the Spotify API to get the details of the playlists by their IDs
    for playlist_id in playlist_ids:
        try:
            playlist = senza_login.playlist(playlist_id)  # Assuming 'senza_login' is a Spotify instance
            playlists.append({
                'id': playlist['id'],
                'name': playlist['name'],
                'owner': playlist['owner']['display_name'],
                'images': playlist.get('images', [{'url': '/static/default-image.jpg'}]),
                'external_urls': playlist.get('external_urls', {}).get('spotify', ''),
            })
        except Exception as e:
            print(f"Error fetching playlist {playlist_id}: {e}")
    
    return playlists
def get_tracks_from_playlist(playlist_id):
    """
    Fetches the tracks for a given playlist and returns a list of track names.
    """
    try:
        playlist = senza_login.playlist_tracks(playlist_id)
        tracks = playlist.get('items', [])
        track_names = set()

        for track in tracks:
            track_name = track['track']['name']
            track_names.add(track_name.lower())  # Normalize track names by converting them to lowercase

        return track_names
    except Exception as e:
        print(f"Error fetching tracks for playlist {playlist_id}: {e}")
        return set()
