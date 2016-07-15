from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import config
from .auth import login_manager
from .data import db

import os
print "test test test"

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')

# create our little application :)
app = Flask(__name__, template_folder=template_dir)
app.config.from_object(config)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

login_manager.init_app(app)

app.secret_key = config.SECRET_KEY

db.init_app(app)

from app import views, models, data
