'''
Author: Mario Bartolomé
Date: Jan 12, 2018
######

Flask app db Models
'''

from frontend.controller import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
	"""
	Database Model for User.
	"""
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(64), index=True, unique=True)
	name = db.Column(db.String(20), index=False)
	surname = db.Column(db.String(20), index=True)
	email = db.Column(db.String(64), index=True, unique=True)
	passwd_hash = db.Column(db.String(128))
	actions = db.relationship('ActionLogs', backref='author', lazy='dynamic')
	drones = db.relationship('Drones', backref='pilot', lazy='dynamic')

	def setPasswd(self, password):
		self.passwd_hash = generate_password_hash(password)

	def checkPasswd(self, password):
		return check_password_hash(self.passwd_hash, password)

	def __repr__(self):
		return '<User {0}> {1}, email: {2}>'.format(self.id, self.username, self.email)


class LoginLogs(db.Model):
	"""
	Database Model for Login logs.
	"""
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

	def __repr__(self):
		return '<Login-{0}> User {1} @ {2}'.format(self.id, self.user_id, self.timestamp)


class IntrusionAttempt(db.Model):
	"""
	Database Model for Intrusion attempts.
	"""
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	provided_user = db.Column(db.String(120))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

	def __repr__(self):
		return '<Intrusion-{0}> User {1} @ {2}'.format(self.id, self.provided_user, self.timestamp)


class Action(db.Model):
	"""
	Database Model for Action descriptors.
	"""
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	description = db.Column(db.String(120))


class ActionLogs(db.Model):
	"""
	Database Model for Actions logs.
	"""
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	action_id = db.Column(db.Integer, db.ForeignKey('action.id'), index=True)

	def __repr__(self):
		return '<ActionLog-{0}> User {1} @ {2}. Performed action: {3}'.format(
			self.id, self.user_id, self.timestamp, self.action.description
		)


class Drones(db.Model):
	"""
	Database Model for Drones.
	"""
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(25), unique=True, nullable=False, index=True)
	location = db.Column(db.String(128))
	url = db.Column(db.String(100), unique=True, nullable=False, index=True)
	controller = db.Column(db.String(64), db.ForeignKey('user.id'), index=True, nullable=False)
	video_port = db.Column(db.Integer, default=8888)
	control_port = db.Column(db.Integer, default=12345)

	def __repr__(self):
		return '<Drone-{0}> {1}, @ {2}, Controlled by: {3}'.format(
			self.id, self.name, self.location, self.controller
		)


@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))
