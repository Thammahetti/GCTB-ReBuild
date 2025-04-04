from flask import Flask
from blueprints.auth import auth_bp
from blueprints.home import home_bp
from blueprints.main_page import main_bp
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from services.model import db, User
import secrets

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)  

# Initialize DB and LoginManager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main_page.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all database tables
with app.app_context():
    db.create_all()

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(main_bp)



if __name__ == "__main__":
    app.run(debug=True, port=5002)
