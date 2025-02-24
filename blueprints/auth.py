from flask import Blueprint, redirect, request, url_for, session, render_template
from services.spotify_oauth import sp_oauth, get_spotify_object
from blueprints.main_page import main_bp
auth_bp = Blueprint('auth', __name__) 

@auth_bp.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)



@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        return redirect(url_for('home.home'))
    return "Errore nella richiesta del codice di autorizzazione."

@auth_bp.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('main_page.main')) 