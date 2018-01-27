'''
Author: Mario Bartolomé
Date: Jan 24, 2018
######

This file aims to provide a simple class to implement MSP protocol.
'''

import serial
import time
import struct



class MSPio:
	"""
	This class provides a quick implementation to get and send data to a serial port using MSP protocol.

	"""

	message = {'preamble': [b'$',b'M'],
	           'toFC': [b'<'],
	           'fromFC': [b'>'],
	           }

	ATTITUDE = 108      # GET attitude (angle x, angle y, heading)
	STATUS = 110        # GET status (battery voltage, consumed power, RSSI, instant current)
	SET_RAW_RC = 200    # SET rc input (injects RC channel, overriding RX input if upd. every second)
	SET_RAW_MOTOR = 214 # SET individual motor value [1000 , 2000]

	def __init__(self, serial_port='/dev/tty.SLAB_USBtoUART', baud_rate=115200):
		"""
		Constructor method for MSPio class.

		:param serial_port: The port to connect to. Defaults to '/dev/tty.SLAB_USBtoUART'.
		:param baud_rate: Speed of the connection in bauds. Defaults to 115200.
		"""
		self._serial = serial.Serial()
		self._serial.port = serial_port
		self._serial.baudrate = baud_rate

		try:
			self._serial.open()
			print("Port {0} successfully opened".format(serial_port))
		except serial.SerialException as err:
			print("Error while opening serial comm: {0}".format(str(err)))
		except FileNotFoundError as err:
			print("Can't find port to open: {0}".format(str(err)))



	def isOpen(self):
		"""
		Checks if serial communication is open.

		:return: True if comm was open, False otherwise.
		"""
		return self._serial.isOpen()

	def close(self):
		"""
		Closes the communication if it was open.

		"""
		if self.isOpen():
			self._serial.close()


	def cleanup(self):
		"""
		Cleans up the remaining buffers.
		:return:
		"""
		self._serial.flushInput()
		self._serial.flushOutput()


	def sendCMD(self, command, data=[], size=0):
		"""
		Sends the given command.

		:param command: The command to send.
		:param data: The data to send. Defaults to an empty list.
		:param size: Size of the data. Defaults to 0.
		"""
		checksum = len(data)
		msg = self.message['preamble'] + self.message['toFC'] + [size] + [command] + data

		# Checksum calc is XOR between <size>, <command> and (each byte) <data>
		msg = struct.pack('<3c2B%iH' % len(data), *msg)

		for i in msg[3:]:
			checksum ^= i

		# Add checksum at the end of the msg
		msg += bytes(chr(checksum), encoding='UTF-8')
		try:
			self._serial.write(msg)
		except serial.SerialException as err:
			print("Could not write to port: {0}".format(str(err)))


	def readResponse(self, command, parse_to=None) -> (bytes, bool):
		"""
		Read FC's response. Remember to use this AFTER calling sendCMD.

		:param command: The command that was sent previously.
		:param parse_to: The format of the response. Defaults to None. If none, raw data to be returned
		:return: FC's response applying parsing method given.
		"""

		response = b''
		status_ok = False
		try:
			if self.isOpen():
				if self._serial.read(3) == b'$M>':  # Seems like a good answer...
					length = struct.unpack('<b', self._serial.read(1))[0]
					response_command = self._serial.read(1)
					if response_command == struct.pack('<b', command):  # and a good command response...
						response = self._serial.read(length)
						if parse_to is not None:
							response = struct.unpack(parse_to, response)
						status_ok = True
					else:
						print('FC seems to be responding to some other command: {0}'.format(struct.unpack('<b', response_command))[0])
				else:
					print("Cant' get a good answer from FC")

		except serial.SerialException as err:

			print("Can't read from port: {0}".format(err))

		finally:

			self._serial.flushInput()
			self._serial.flushOutput()

		return response, status_ok





	def readAttitude(self) -> dict:
		"""
		Reads the attitude values from the IMU.
		Angle on X axis.
		Angle on Y axis.
		Heading of the device.

		:return: a dictionary containing those values, and a timestamp
		"""
		command = self.ATTITUDE

		attitude = {'x':0, 'y':0, 'heading':-361, 'timestamp':0}
		self.sendCMD(command)
		parse_to = '<3h'  # returns 3 int16, therefore 6 bytes to read on 2 by 2
		tmp, status_ok = self.readResponse(command, parse_to)
		if status_ok:
			attitude['x'] = tmp[0] / 10.0
			attitude['y'] = tmp[1]/10.0
			attitude['heading'] = tmp[2]
			attitude['timestamp'] = time.time()

		return attitude


	def readStatus(self) -> dict:
		"""
		Reads the analog sensors from the FC.
		Battery voltage.
		Consumed power.
		RSSI.
		Instant current.

		:return: a dictionary containing those values, and a timestamp
		"""
		command = self.STATUS

		status = {'vbat': 0.0, 'cons_mah': 0, 'RSSI': 0, 'current': 0}
		self.sendCMD(command)
		parse_to = '<B3H'
		tmp, status_ok = self.readResponse(command, parse_to)
		if status_ok:
			status['vbat'] = tmp[0]/10
			status['cons_mah'] = tmp[1]
			status['RSSI'] = tmp[2]
			status['current'] = tmp[3]

		return status


# To test it:
if __name__ == '__main__':
	ser = MSPio()
	import signal
	import sys
	def signal_handler(signal, frame):
		print('\nCleaning up...')
		ser.cleanup()

		ser.close()
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)

	if ser.isOpen():

		while True:
			print("Readings: {0} // Voltage: {1}".format(ser.readAttitude(), ser.readStatus()['vbat']))
			time.sleep(0.1)
	
