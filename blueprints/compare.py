# compare.py
from flask import Blueprint, request, render_template
import plotly.graph_objects as go
import plotly.express as px
from services.spotify_oauth import sp_oauth
import spotipy
from collections import Counter
from datetime import datetime

compare_bp = Blueprint('compare', __name__)

senza_login = spotipy.Spotify(client_credentials_manager=sp_oauth)

def get_tracks_info(playlist_id):
    try:
        playlist = senza_login.playlist_tracks(playlist_id)
        items = playlist.get('items', [])
        tracks_info = []
        for item in items:
            track = item['track']
            if not track:
                continue
            track_data = {
                'name': track['name'],
                'id': track['id'],
                'popularity': track.get('popularity', 0),
                'artists': [artist['name'] for artist in track['artists']],
                'artist_ids': [artist['id'] for artist in track['artists']],
                'release_date': track['album'].get('release_date', '1900-01-01')
            }
            tracks_info.append(track_data)
        return tracks_info
    except Exception as e:
        print(f"Error fetching tracks: {e}")
        return []

def get_artist_genres(artist_ids):
    genres = []
    for artist_id in artist_ids:
        try:
            artist = senza_login.artist(artist_id)
            genres.extend(artist.get('genres', []))
        except:
            continue
    return genres

def get_common_tracks(tracks1, tracks2):
    names1 = set([t['name'].lower() for t in tracks1])
    names2 = set([t['name'].lower() for t in tracks2])
    common = names1 & names2
    return common, len(common)

def get_common_artists(tracks1, tracks2):
    artists1 = [artist for t in tracks1 for artist in t['artists']]
    artists2 = [artist for t in tracks2 for artist in t['artists']]
    common = set(artists1) & set(artists2)
    freq1 = Counter([a for a in artists1 if a in common])
    freq2 = Counter([a for a in artists2 if a in common])
    return common, freq1, freq2

def get_average_popularity(tracks):
    if not tracks:
        return 0
    return sum([t['popularity'] for t in tracks]) / len(tracks)

def get_release_years(tracks):
    years = []
    for t in tracks:
        try:
            year = datetime.strptime(t['release_date'], '%Y-%m-%d').year
        except:
            try:
                year = int(t['release_date'][:4])
            except:
                year = 1900
        years.append(year)
    return Counter(years)

@compare_bp.route('/compare/<string:graph_type>')
def generate_graph(graph_type):
    playlist_ids = request.args.get('playlist_ids')
    if not playlist_ids:
        return "Missing playlist_ids", 400

    playlist_ids = playlist_ids.split(',')
    if len(playlist_ids) != 2:
        return "Need exactly two playlist IDs", 400

    tracks1 = get_tracks_info(playlist_ids[0])
    tracks2 = get_tracks_info(playlist_ids[1])

    playlist1 = senza_login.playlist(playlist_ids[0])
    playlist2 = senza_login.playlist(playlist_ids[1])
    name1 = playlist1['name']
    name2 = playlist2['name']

    if graph_type == "common_tracks":
        common_tracks, common_count = get_common_tracks(tracks1, tracks2)
        similarity_percentage = (common_count / (min(len(tracks1), len(tracks2)) + 0.1)) * 100
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[name1, name2], y=[len(tracks1), len(tracks2)], name="Total Tracks"))
        fig.add_trace(go.Bar(x=[name1, name2], y=[common_count, common_count], name="Common Tracks"))
        fig.update_layout(barmode="group", title=f"Tracks in Common ({similarity_percentage:.2f}%)")
        return fig.to_html(include_plotlyjs=False, full_html=False)

    elif graph_type == "common_artists":
        common_artists, freq1, freq2 = get_common_artists(tracks1, tracks2)
        fig = go.Figure()
        for artist in common_artists:
            fig.add_trace(go.Bar(name=artist, x=[name1, name2], y=[freq1.get(artist, 0), freq2.get(artist, 0)]))
        fig.update_layout(barmode="group", title="Common Artists Frequency")
        return fig.to_html(include_plotlyjs=False, full_html=False)

    elif graph_type == "popularity":
        pop1 = get_average_popularity(tracks1)
        pop2 = get_average_popularity(tracks2)
        fig = px.bar(x=[name1, name2], y=[pop1, pop2], labels={'x': 'Playlist', 'y': 'Average Popularity'}, title="Average Track Popularity")
        return fig.to_html(include_plotlyjs=False, full_html=False)

    elif graph_type == "genres":
        genre1 = get_artist_genres([aid for t in tracks1 for aid in t['artist_ids']])
        genre2 = get_artist_genres([aid for t in tracks2 for aid in t['artist_ids']])
        genre_freq1 = Counter(genre1)
        genre_freq2 = Counter(genre2)
        common_genres = set(genre_freq1) | set(genre_freq2)
        fig = go.Figure()
        for genre in list(common_genres)[:10]:
            fig.add_trace(go.Bar(name=genre, x=[name1, name2], y=[genre_freq1.get(genre, 0), genre_freq2.get(genre, 0)]))
        fig.update_layout(barmode="group", title="Top Genres Distribution")
        return fig.to_html(include_plotlyjs=False, full_html=False)

    elif graph_type == "temporal":
        years1 = get_release_years(tracks1)
        years2 = get_release_years(tracks2)
        all_years = sorted(set(years1) | set(years2))
        fig = go.Figure()
        fig.add_trace(go.Bar(name=name1, x=all_years, y=[years1.get(y, 0) for y in all_years]))
        fig.add_trace(go.Bar(name=name2, x=all_years, y=[years2.get(y, 0) for y in all_years]))
        fig.update_layout(barmode="group", title="Release Year Distribution")
        return fig.to_html(include_plotlyjs=False, full_html=False)

    return "Invalid graph type", 400