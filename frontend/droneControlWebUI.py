'''
Author: Mario Bartolomé
Date: Jan 12, 2018
######

Flask app init
'''
from frontend.controller import app, socketio


if __name__ == '__main__':
	socketio.run(app, log_output=True)
