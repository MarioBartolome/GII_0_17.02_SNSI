'''
Author: Mario Bartolomé
Date: Jan 12, 2018
######

Flask app Controller
'''

from frontend.controller import app, db
from flask import render_template, flash, redirect, url_for, request
from frontend.view.login import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from frontend.model.models import User, LoginLogs, IntrusionAttempt
from datetime import timedelta
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
	"""
	Index site for logged users.

	"""
	if current_user.is_authenticated:
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
	if current_user.is_authenticated:
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
	if current_user.is_authenticated:
		logout_user()
		flash('User logged out. Bye!', category='message')
		return redirect(url_for('login'))
	else:
		flash('Humm... that is weird... You were not logged in', category='warning')
		return redirect(url_for('login'))


def video_feed():
	drone_url = current_user.drones.first().url
	return drone_url
