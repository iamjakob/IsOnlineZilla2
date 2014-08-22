from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask.ext.cache import Cache
import os
from flask.ext.login import LoginManager
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
app.secret_key = "askdlasjdklklassd"
#cache = Cache(app,config={'CACHE_TYPE': 'simple'})

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)

from app import views