'''
Author: Mario Bartolomé
Date: Apr 1, 2018
######

Synchronized Remote Control server for agent channel input
'''


import socket, sys, json, struct
from threading import Lock, Thread


class RemoteServer(Thread):

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
		super().__init__()
		self._address = addr
		self._port = port
		self._manualEnabled = False
		self._remoteInput = None
		self._rILock = Lock()
		self._channel_names = ['Ax0', 'Ax1', 'Ax2', 'Ax3', 'Ax4']
		print("RemoteControl server ready to start")

	def run(self):
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
				chck = self.synchronized(self.retrieveInput, conn)
				if not chck:
					print("<RemoteServer> Client disconnected. Closing resources...")
					self.synchronized(self.disconnection)
					print("Awaiting clients..")
					conn, client_address = stream.accept()
					print("Hello! New client from {0}".format(client_address[0]))
					'''self.synchronized(self.retrieveInput, conn, blocking=False)
				print(self.getChannels()) # Uncomment both lines to get output.'''
			except ConnectionResetError as err:
				print("<RemoteServer> Connection abruptly closed from client", err)
				self.disconnection()


	def retrieveInput(self, conn: socket):
		"""
		Gets the values from the connection.

		:param conn: The connection.
		:return: True or False depending if it was able to read the socket
		"""
		msg_length_b = conn.recv(2)
		if len(msg_length_b) == 2:
			msg_length = struct.unpack('<H', msg_length_b)[0]
			self._remoteInput = conn.recv(msg_length)
			self._manualEnabled = True
			return True
		else:
			return False

	def disconnection(self):
		"""
		Disconnects from connection socket.
		"""

		self._manualEnabled = False
		self._remoteInput = None


	def isManualEnabled(self):
		"""
		Returns if manual mode is enabled.
		:return: True or False
		"""
		return self._manualEnabled


	def getLock(self):
		"""
		For synchronization purposes.
		:return: The instance Lock
		"""
		return self._rILock


	def getChannels(self) -> list:
		"""
		Decodes socket input.
		:return: raw channel values
		"""
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

		self._rILock.acquire(blocking=blocking)
		out = method(args) if args else method()
		self._rILock.release()
		return out


if __name__ == "__main__":
	server = RemoteServer()
	server.start()
