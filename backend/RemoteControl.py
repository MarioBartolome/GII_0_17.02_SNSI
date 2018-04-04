'''
Author: Mario Bartolomé
Date: Apr 1, 2018
######

Synchronized Remote Control server for agent channel input
'''


import socket, sys, json, struct
from threading import Lock

class RemoteServer:

	def __init__(
			self,
			addr: str = '0.0.0.0',
			port: int = 12345):
		"""
		Constructor for RemoteServer class.
		:param addr: Address to bind the server.
		:type addr: str
		:param port: Port to use by the server.
		:type port: int
		"""
		self._address = addr
		self._port = port
		self._manualEnabled = False
		self._remoteInput = None
		self._rILock = Lock()
		self._channel_names = ['Ax0', 'Ax1', 'Ax2', 'Ax3', 'Ax4']
		print("RemoteControl server ready to start")

	def start(self):
		"""
		Starts the RemoteServer control.

		"""

		try:
			stream = socket.socket()
			stream.bind((self._address, self._port))
			stream.listen(0)
			print("Awaiting clients..")
			conn, client_address = stream.accept()
			print("Hello! New client from {0}".format(client_address[0]))
		except socket.error as err:
			print('Could not bind socket! <err {0}>: {1}'.format(err.errno, str(err)))
			self._manualEnabled = False
			sys.exit(1)


		while True:
			try:
				self.synchronized(self.retrieveInput, conn, blocking=False)
				if self._remoteInput == b'':
					print("<RemoteServer - {0}> Client disconnected. Closing resources...")
					self.synchronized(self.disconnection)
					print("Awaiting clients..")
					conn, client_address = stream.accept()
					print("Hello! New client from {0}".format(client_address[0]))
				# print(self._remoteInput)
				print(self.getChannels())
			except ConnectionResetError as err:
				print("<RemoteServer> Connection abruptly closed from client", err)
				self.disconnection()


	def retrieveInput(self, conn: socket):
		"""
		Gets the values from the connection.

		:param conn: The connection.
		"""
		msg_length = struct.unpack('<H', conn.recv(2))[0]
		self._remoteInput = conn.recv(msg_length)
		self._manualEnabled = True


	def disconnection(self):
		"""
		Disconnects from connection socket.
		"""

		self._manualEnabled = False
		self._remoteInput = None


	def isManualEnabled(self):
		return self._manualEnabled


	def getChannels(self):
		input_decoded = json.JSONDecoder().decode(self._remoteInput.decode('utf-8'))
		raw_channels = [round(float(input_decoded[key])) for key in self._channel_names]

		return raw_channels

	def synchronized(self, method, args=None, blocking=True):
		"""
		Synchronized wrapper for methods.

		:param method: method to be called in a sync way.
		:param args: argument for the method.
		:param blocking: sets if the lock should be blocking.
		:return: the output from the method
		"""

		rILock = Lock()
		rILock.acquire(blocking=blocking)
		out = method(args) if args else method()
		rILock.release()
		return out


if __name__ == "__main__":
	server = RemoteServer()
	server.start()
