from backend.autoControllers import abcControllerPID
from typing import List


class YawController(abcControllerPID.abcControllerPID):

	def __init__(self,
	             upper_limit: int = 1600,
	             lower_limit: int = 1400,
	             kP: float = 0.02,
	             kI: float = 0.0,
	             kD: float = 0.01
	             ):

		super(YawController, self).__init__(kP, kI, kD, upper_limit, lower_limit)
		self.setActualRAWRC(1500)

	def setMeasurement(self, measurement: int):
		"""
		Sets the real measurement.
		:param measurement: The measurement taken from the heading sensor.
		"""
		self._measurement = measurement

	def getChannels(self) -> List:
		"""
		Returns the channels values as a list.
		:return: a list with the RAW RC values.
		"""
		return [self.computePID()]

	def getLock(self):
		return None
