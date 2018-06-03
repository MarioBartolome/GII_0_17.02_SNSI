from backend.autoControllers import abcControllerPID
from typing import List, Dict


class InclinationController(abcControllerPID.abcControllerPID):

	def __init__(self,
	             upper_limit: int = 1600,
	             lower_limit: int = 1400,
	             kP: float = 0.04,
	             kI: float = 0.0,
	             kD: float = 0.01
	             ):

		super(InclinationController, self).__init__(kP, kI, kD, upper_limit, lower_limit)
		self.setActualRAWRC(1500)

	def setMeasurement(self, measurement: List[Dict, int]):
		"""
		Sets the real measurement.
		:param measurement: The measurement[0] taken from Accel/Gyro and the desired target, measurement[1]
		"""
		self._measurement = measurement[0]['x']
		self._target = measurement[1]

	def getChannels(self) -> List:
		"""
		Returns the channels values as a list.
		:return: a list with the RAW RC values.
		"""
		return [self.computePID()]

	def getLock(self):
		return None
