from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from Qtalk.config import app_secret_key, db_password, db_name, db_server, db_username


app = Flask(__name__)
app.config['SECRET_KEY'] = app_secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_username}:{db_password}@{db_server}/{db_name}?charset=utf8mb4'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "برای دسترسی ب این صفحه باید وارد شوید"
login_manager.login_message_category = "info"

from Qtalk import routes
