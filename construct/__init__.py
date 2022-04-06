from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from flask_login import LoginManager
from datetime import date, timedelta
from flask_mail import Mail, Message
import plotly






app = Flask(__name__)
app.secret_key = 'df068fc9da4421a70764842f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///construct.db'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sdousmanflask@gmail.com'
app.config['MAIL_PASSWORD'] = 'Redbull12!123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
db = SQLAlchemy(app)

# Function that initializes the db and creates the tables
def db_init(app):
    db.init_app(app)

    # Creates the logs tables if the db doesnt already exist
    with app.app_context():
        db.create_all()


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
mail= Mail(app)






from construct import routes