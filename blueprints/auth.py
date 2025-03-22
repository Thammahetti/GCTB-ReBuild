from flask import Blueprint, redirect, request, url_for, session, render_template
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from services.model import db, User
from services.spotify_oauth import sp_oauth, get_spotify_object
from blueprints.main_page import main_bp

auth_bp = Blueprint('auth', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        cognome 
        token_info = sp_oauth.get_access_token(code)
        session['spotify_token'] = token_info
        return redirect(url_for('home.home1'))
    return "Error during authorization."

# Logout 
@auth_bp.route('/logout_spotify')
def logout_spotify():
    session.pop('spotify_token', None)
    return redirect(url_for('main_page.main_home'))

@auth_bp.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('main_page.main_home'))
