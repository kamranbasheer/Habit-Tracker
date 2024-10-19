from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize the Flask application
app = Flask(__name__)

# Configure the database
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import routes after creating the app
from app import routes

from app import app, db, login_manager
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
