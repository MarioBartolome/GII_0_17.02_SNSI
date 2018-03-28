"""
Author: Mario Bartolomé
Date: Mar 12, 2018
######

This file aims to provide a simple init for the Drone Control System.
"""

from flask import Flask
from frontend.model.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


template_path = '../view/templates'
static_path = '../view/static'
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from frontend.controller import routes
