# home.py
from flask import Blueprint, redirect, request, url_for, session, render_template, jsonify
import spotipy
from services.spotify_oauth import sp_oauth, get_spotify_object
from spotipy.oauth2 import SpotifyClientCredentials
from services.model import db, Playlist, User

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

def get_top_artists(query):
    # Search for top artists based on the query
    results = senza_login.search(q=query, type='artist', limit=10)
    artists = results.get('artists', {}).get('items', [])

    artist_names = [artist['name'] for artist in artists]
    artist_popularity = [artist['popularity'] for artist in artists]

    return {
        'data': [{
            'type': 'bar',
            'x': artist_names,
            'y': artist_popularity,
            'name': 'Top Artists',
            'marker': {'color': 'rgb(100, 100, 255)'}
        }],
        'layout': {
            'title': 'Top Artists',
            'xaxis': {'title': 'Artists'},
            'yaxis': {'title': 'Popularity'}
        }
    }

def get_top_albums(query):
    # Search for top albums based on the query
    results = senza_login.search(q=query, type='album', limit=10)
    albums = results.get('albums', {}).get('items', [])

    album_names = [album['name'] for album in albums]
    
    # Ensure that 'popularity' exists in the album object
    album_popularity = [album.get('popularity', 0) for album in albums]  # Default to 0 if no popularity data

    return {
        'data': [{
            'type': 'bar',
            'x': album_names,
            'y': album_popularity,
            'name': 'Top Albums',
            'marker': {'color': 'rgb(255, 100, 100)'}
        }],
        'layout': {
            'title': 'Top Albums',
            'xaxis': {'title': 'Albums'},
            'yaxis': {'title': 'Popularity'}
        }
    }


def get_genre_distribution(query):
    # Search for top artists based on the query
    results = senza_login.search(q=query, type='artist', limit=10)
    artists = results.get('artists', {}).get('items', [])

    genres = []
    for artist in artists:
        genres.extend(artist.get('genres', []))  # Collect genres of each artist

    # Count the frequency of each genre
    genre_count = {genre: genres.count(genre) for genre in set(genres)}

    # Prepare the genre data for graphing
    genre_names = list(genre_count.keys())
    genre_frequencies = list(genre_count.values())

    return {
        'data': [{
            'type': 'bar',
            'x': genre_names,
            'y': genre_frequencies,
            'name': 'Genre Distribution',
            'marker': {'color': 'rgb(50, 150, 50)'}
        }],
        'layout': {
            'title': 'Genre Distribution',
            'xaxis': {'title': 'Genres'},
            'yaxis': {'title': 'Frequency'}
        }
    }




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

        # Get graph data for artists, albums, and genres without needing login
        top_artists_data = get_top_artists(query)  # You can call this directly using `senza_login`
        top_albums_data = get_top_albums(query)
        genre_data = get_genre_distribution(query)

        return render_template('index.html', playlists=cleaned_playlists, query=query,
                               artist_graph=top_artists_data, album_graph=top_albums_data, genre_graph=genre_data)

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
    # Ensure the user is logged in (check session)
    if not session.get('user_id'):
        return redirect(url_for('auth.logout_spotify'))  # Redirect if no user is logged in

    user_id = session.get('user_id')  # Get the user ID from the session

    # Query the playlists saved by the user from the database
    playlists = Playlist.query.filter_by(user_id=user_id).all()

    # If no playlists found, return an appropriate message
    if not playlists:
        return render_template('my_playlists.html', playlists=None, message="You haven't added any playlists yet.")
    
    # Initialize the Spotify instance for searching (without user login)
    sp = senza_login  # This is the Spotify instance without user authentication

    playlist_details = []
    
    for playlist in playlists:
        try:
            # Use the playlist method to fetch playlist details directly using the playlist_id
            spotify_playlist = sp.playlist(playlist.playlist_id)  # Fetch the playlist details directly
            
            playlist_details.append({
                'name': spotify_playlist['name'],
                'url': spotify_playlist['external_urls']['spotify'],
                'image_url': spotify_playlist['images'][0]['url'] if spotify_playlist['images'] else '/static/default-image.jpg'
            })
        except Exception as e:
            # If there is an error fetching the playlist, log it and skip it
            print(f"Error fetching playlist {playlist.playlist_id}: {e}")
    
    return render_template('my_playlists.html', playlists=playlist_details)

