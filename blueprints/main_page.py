from flask import Blueprint, redirect, request, url_for, session, render_template
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from services.model import db, User

main_bp = Blueprint('main_page', __name__)



@main_bp.route('/home', endpoint='main_home')
@login_required
def home():
    return render_template('index.html', error=None, user=current_user)

