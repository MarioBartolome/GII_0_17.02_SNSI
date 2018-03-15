'''
Author: Mario Bartolomé
Date: Jan 12, 2018
######

Flask app LoginForm
'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
	"""
	A simple login form for users.

	"""
	user = StringField('Username', validators=[DataRequired()])
	passwd = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Log in')
