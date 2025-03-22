from flask import Blueprint, redirect, request, url_for, session, render_template
from services.spotify_oauth import sp_oauth, get_spotify_object
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

main_bp = Blueprint('main_page', __name__) 

@main_bp.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Prendere i dati dal database
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        username = request.form['username'] 
        password = request.form['password']
        password_hash = generate_password_hash(password)

        #Controllo per vedere se esiste già
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già in uso.")

        new_user = User( nome=nome ,cognome=cognome, email= email, username=username, password=password_hash )
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login1'))
    return render_template('register.html', error=None)

@main_bp.route('/login1', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        #prende dati dal form
        username = request.form['username'] 
        password = request.form['password']
        #cerca user su db
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home.home'))
        return render_template('login.html', error="Credenziali non valide.") 
    return render_template('login.html', error=None)

@main_bp.route('/home', endpoint='main_home')
@login_required
def home():
    return render_template('index.html', error=None)
