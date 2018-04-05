'''
Author: Mario Bartolomé
Date: Jan 12, 2018
######

Flask app Controller
'''

from frontend.controller import app, db, socketio
from flask import render_template, flash, redirect, url_for, request
from frontend.view.login import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from frontend.model.models import User, LoginLogs, IntrusionAttempt, ActionLogs
from datetime import timedelta
from werkzeug.urls import url_parse
import socket, json, sys, struct
# Uncomment to use CertBot to get SSL certs to HTTP*S*
# import send_from_directory


rControlSocket = None
remoteEnabled = False
@app.route('/')
@app.route('/index')
@login_required
def index():
	"""
	Index site for logged users.

	"""
	if userIsAuthenticated():
		user = {'username': current_user.name}
		video_urn = video_feed()
	else:
		user = {'username': 'unknown user'}
		video_urn = ''

	return render_template('index.html', user=user, video_url=video_urn)


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""
	Allows a user to login.

	:return: If successful redirects to index, else to login page.
	"""
	if userIsAuthenticated():
		flash('Already logged in! Welcome', category='message')
		return redirect(url_for('index'))
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.user.data).first()
		if user is None or not user.checkPasswd(form.passwd.data):
			flash('Invalid username or password.', category='error')
			flash('Intrusion attempt logged', category='warning')
			db.session.add(IntrusionAttempt(provided_user=form.user.data))
			db.session.commit()
			return redirect(url_for('login'))
		else:
			login_user(user, remember=form.remember_me.data, duration=timedelta(minutes=10))
			db.session.add(LoginLogs(user_id=user.id))
			db.session.commit()
			flash('Logon successful. Welcome', category='message')
			next_page = request.args.get('next')
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('index')

			return redirect(next_page)

	return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
	"""
	Allows a user to logout.

	:return: If successful redirects to login.
	"""
	if userIsAuthenticated():
		logout_user()
		flash('User logged out. Bye!', category='message')
		return redirect(url_for('login'))
	else:
		flash('Humm... that is weird... You were not logged in', category='warning')
		return redirect(url_for('login'))


def userIsAuthenticated():
	return current_user.is_authenticated

@socketio.on('connect')
@login_required
def connection():
	if userIsAuthenticated():
		drone = current_user.drones.first()
		url = drone.url
		port = drone.control_port

		print('Attempting to connect to drone Remote Control System on ' + url)
		db.session.add(ActionLogs(user_id=current_user.id, action_id=1))
		db.session.commit()
		global rControlSocket
		rControlSocket = socket.socket()
		try:
			rControlSocket.connect((url, port))
			global remoteEnabled
			remoteEnabled = True
		except ConnectionError as e:
			print("Error connecting to socket!", e, file=sys.stderr)
			raise e
	else:
		flash('You should not try to enable manual control without authenticating first', category='error')
		return redirect(url_for('login'))


@socketio.on('disconnect')
def disconnection():
	db.session.add(ActionLogs(user_id=current_user.id, action_id=2))
	db.session.commit()
	global rControlSocket, remoteEnabled
	try:
		remoteEnabled = False
		rControlSocket.close()
	except ConnectionError as e:
		print("Error while closing socket!", e, file=sys.stderr)


@socketio.on('axisInput')
@login_required
def control_info_recv(info):
	global rControlSocket, remoteEnabled
	if remoteEnabled:
		try:
			msg = bytes(json.dumps(info), encoding='UTF-8')
			msg_length = len(msg)
			rControlSocket.send(struct.pack('<H', msg_length) + msg)
		except ConnectionError as e:
			print("Error connecting to socket!", e, file=sys.stderr)
			emitConnectionError()
			disconnection()

def emitConnectionError():
	socketio.emit('connect_error')

def video_feed():
	drone = current_user.drones.first()
	url = drone.url
	port = drone.video_port
	video_url = url + ':' + str(port) + '/webrtc'
	return video_url

# Uncomment to use CertBot to get SSL certs to HTTP*S*
# @app.route('/.well-known/<path:path>')
# def send_js(path):
# 	return send_from_directory('.well-known', path)
