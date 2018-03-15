'''
Author: Mario Bartolomé
Date: Jan 14, 2018
######

Flask app config
'''
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.getenv('TOKEN_KEY', default='fCRZ4dYVOjNL0oP6luMevORr')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'database.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
