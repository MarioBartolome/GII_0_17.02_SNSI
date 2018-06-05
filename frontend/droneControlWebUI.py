'''
Author: Mario Bartolomé
Date: Jan 12, 2018
######

Flask app init
'''
from frontend.controller import app, socketio
HOST_ADDRESS = '127.0.0.1'

if __name__ == '__main__':
	socketio.run(app, log_output=True, host=HOST_ADDRESS, certfile='../private/fullchain.pem', keyfile='../private/privkey.pem')
