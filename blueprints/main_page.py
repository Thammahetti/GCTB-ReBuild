from flask import Blueprint, redirect, request, url_for, session, render_template
from services.spotify_oauth import sp_oauth, get_spotify_object

main_bp = Blueprint('main_page', __name__) 


@main_bp.route('/')
def index():
    return render_template('index.html') 

