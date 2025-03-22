from flask import Blueprint, redirect, request, url_for, session, render_template
import spotipy
from services.spotify_oauth import sp_oauth, get_spotify_object
from spotipy.oauth2 import SpotifyClientCredentials

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
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('auth.logout_spotify'))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    brani = sp.playlist_items(playlist_id)
    brani_specifici = brani['items']
    return render_template('brani.html', brani=brani_specifici)

@home_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')

    if query:
        results = senza_login.search(q=query, type='playlist', limit=10)
        
        # Controllo che results non sia None e che contenga playlist
        playlists = results.get('playlists', {}).get('items', [])

        cleaned_playlists = []  # Lista per memorizzare solo le playlist valide

        for playlist in playlists:
            if playlist is None:  # Controllo che la playlist non sia None
                continue

            # Assicura che 'images', 'name' e 'owner' siano presenti
            playlist['images'] = playlist.get('images', [{'url': '/static/default-image.jpg'}])
            playlist['name'] = playlist.get('name', 'Unknown Playlist')
            playlist['owner'] = playlist.get('owner', {'display_name': 'Unknown'})

            cleaned_playlists.append(playlist)  # Aggiunge solo playlist valide
        
    else:
        cleaned_playlists = []

    return render_template('index.html', playlists=cleaned_playlists, query=query)

