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
STORAGE_CONNECTION_STRING = 'BlobEndpoint=https://constructify.blob.core.windows.net/;QueueEndpoint=https://constructify.queue.core.windows.net/;FileEndpoint=https://constructify.file.core.windows.net/;TableEndpoint=https://constructify.table.core.windows.net/;SharedAccessSignature=sv=2020-08-04&ss=f&srt=sco&sp=rwdlc&se=2023-04-10T03:23:17Z&st=2022-04-09T19:23:17Z&spr=https,http&sig=s7GEen6scx0kjjH2GeRCJODr8C59u8jCRv%2FmBcHS%2FaE%3D'
db = SQLAlchemy(app)
UPLOAD_FOLDER = 'construct/static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Function that initializes the db and creates the tabless
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