from flask import Flask
from blueprints.auth import auth_bp
from blueprints.home import home_bp
from blueprints.main_page import main_bp
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"  

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main_page.login1'  

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(main_bp)
 
if __name__ == "__main__":
    app.run(debug=True)