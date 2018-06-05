from unittest import TestCase
from backend.comms.MultiWiiProtocol import MSPio
import time


ser = MSPio()
time.sleep(2)
if ser.isOpen():
	ser._serial.read_all()

class TestMSPio(TestCase):

	def test_readAttitude(self):
		self.assertTrue(all(key in ['x', 'y', 'heading', 'timestamp'] for key in ser.readAttitude().keys()))

	def test_readStatus(self):
		self.assertTrue(all(key in ['vbat', 'cons_mah', 'RSSI', 'current'] for key in ser.readStatus().keys()))
