from flask import Blueprint, redirect, request, url_for, session, render_template
import spotipy
from services.spotify_oauth import sp_oauth, get_spotify_object

home_bp = Blueprint('home', __name__) 

@home_bp.route('/home')
def home():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('auth.login')) 

    sp = get_spotify_object(token_info)
    user_info = sp.current_user()
    playlists = sp.current_user_playlists() 
    playlists_info = playlists['items'] 
    
    return render_template('home.html', user_info=user_info, playlists=playlists_info) 

@home_bp.route('/playlist/<playlist_id>')
def playlist_details(playlist_id):
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('auth.login'))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    brani = sp.playlist_items(playlist_id)
    brani_specifici = brani['items']
    return render_template('brani.html', brani=brani_specifici)

@home_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')  
    token_info = session.get('token_info', None)
    
    if not token_info:
        return redirect(url_for('auth.login'))

    sp = get_spotify_object(token_info)
    
    if query:
        results = sp.search(q=query, type='track', limit=10)
        tracks = results['tracks']['items']
    else:
        tracks = []  

    return render_template('index.html', tracks=tracks, query=query)