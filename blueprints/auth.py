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
        cognome = request.form['cognome']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già in uso.")

        new_user = User(nome=nome, cognome=cognome, email=email, username=username, password=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main_page.login'))
    return render_template('register.html', error=None)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session['user_id'] = user.id  
            session['username'] = user.username  
            return redirect(url_for('main_page.main_home')) 
        
        return render_template('login.html', error="Credenziali non valide.")
    
    return render_template('login.html', error=None)


@auth_bp.route('/login_spotify')
def login_spotify():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)  

# Callback 
@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
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
