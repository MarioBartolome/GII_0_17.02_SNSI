from backend import abcControllerPID
from typing import List


class AltitudeController(abcControllerPID.abcControllerPID):

	def __init__(self,
	             upper_Limit: int = 1800,
	             lower_limit: int = 1000,
	             kP: float = 0.01,
	             kI: float = 0.00,
	             kD: float = 0.01):

		super(AltitudeController, self).__init__(kP, kI, kD, upper_Limit, lower_limit)

		self._available = False

	def setTarget(self, target: int):
		"""
		Sets target to achieve.
		:param target: The target to achieve.
		:type: int
		"""
		self._target = target

	def setMeasurement(self, measurement: List[int]):
		"""
		Sets the real measurement.
		:param measurement: The measurement taken.
		"""
		self._measurement = measurement[0]

	def setActualRAWRC(self, actualRAWRC: int):
		"""
		Sets the actual RAW RC sent to the channel.
		:param actualRAWRC:
		:return:
		"""
		self._actualRAWRC = actualRAWRC

	def setAvailability(self, av: bool):
		"""
		Sets the availability of the controller.
		:param av: True or False
		"""
		self._available = av

	def getChannels(self) -> List:
		"""
		Returns the channels values as a list.
		:return: a list with the RAW RC values.
		"""
		return [self.computePID()]

	def isAvailable(self):
		"""
		Returns if the controller is ready.
		:return: True or False
		"""
		return self._available

	def getLock(self):
		return None
