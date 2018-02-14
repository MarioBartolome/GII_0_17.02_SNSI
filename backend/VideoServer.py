'''
Author: Mario Bartolomé
Date: Jan 24, 2018
######

This file aims to provide a simple, and efficient, video transmission model for Raspberry Pi's Camera
'''

import socket, sys
import picamera
import threading

class VideoServer(threading.Thread):

	def __init__(
			self,
			addr:str = '0.0.0.0',
			port:int = 12345):
		"""
		Constructor for VideoServer class.
		:param addr: Address to bind the server.
		:type addr: str
		:param port: Port to use by the server.
		:type port: int
		"""
		super(VideoServer, self).__init__()
		self._address = addr
		self._port = port
		print("Video server ready to start")

	def startVideoServer(self):
		"""
		Starts the VideoServer stream.

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
			sys.exit()

		camera = VideoStreamer(conn)
		camera.run()

		while True:
			try:
				response = conn.recv(1024)
				if response == b'':
					print("<VideoServer - {0}> Client {1} disconnected. Closing resources..."
					      .format(self.name, client_address[0]))
					camera.stop()
					stream.shutdown(socket.SHUT_WR)
					# gracefullRestart(camera, stream)
					print("Awaiting clients..")
					conn, client_address = stream.accept()
					print("Hello! New client from {0}".format(client_address[0]))
					camera.setStream(conn)
					camera.run()
			except ConnectionResetError as err:
				print("<VideoServer - {0}> Connection abruptly closed from client"
				      .format(self.name))


class VideoStreamer:

	def __init__(self, stream: socket):
		"""
		Constructor for the VideoStreamer
		:param stream: The stream to record video to.
		:type stream: socket.
		"""
		self._camera = picamera.PiCamera()
		self._camera.resolution = (640, 360)
		self._camera.framerate = 18
		self._stream = stream

	def setStream(self, stream: socket):
		"""
		Sets camera stream output.

		:param stream: The socket to write to.
		:type stream: socket
		"""
		self._stream = stream

	def run(self):
		"""
		Starts to write video to the chosen stream.

		"""

		self._stream = self._stream.makefile('wb')
		self._camera.start_recording(self._stream, format='h264')

	def stop(self):
		"""
		Stops recording and closes all related resources.

		"""
		try:
			try:
				self._camera.stop_recording()
			except BrokenPipeError as err:
				print('<camera-stream> Broken stream: {0}'.format(str(err)))
				self._camera.stop_recording()
			finally:
				self._stream.close()
		except BrokenPipeError:
			pass


if __name__ == '__main__':
	server = VideoServer()
	server.startVideoServer()
