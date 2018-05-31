import abc


class abcControllerPID(object, metaclass=abc.ABCMeta):
	"""
	This class provides few methods to be implemented so it can be controlled making use
	of the ctrlWrapper. Classes implementing this AbstractClass will be treated as prioritizedController.

	"""
	def __init__(self, kP: float, kI: float, kD: float, upper_Limit: int, lower_limit: int):
		"""
		Constructor for a PID system related to ctrlWrapper.

		:param kP:
		:param kI:
		:param kD:
		:param upper_Limit:
		:param lower_limit:
		"""
		self._kP = kP
		self._kI = kI
		self._kD = kD
		self._previous_error = 0.0
		self._acc_error = 0.0
		self._error = 0.0

		self._target = 0.0
		self._measurement = 0.0
		self._actualRAWRC = 1000

		self._upperLimit = upper_Limit
		self._lowerLimit = lower_limit

		self._available = False

	@abc.abstractmethod
	def getChannels(self):
		raise NotImplementedError('This class must implement a way to get which channels it is controlling')

	def isAvailable(self):
		"""
		Returns if the controller is ready.
		:return: True or False
		"""
		return self._available

	def setAvailability(self, av: bool):
		"""
		Sets the availability of the controller.
		:param av: True or False
		"""
		self._available = av

	def setTarget(self, target: int):
		"""
		Sets target to achieve.
		:param target: The target to achieve.
		:type: int
		"""
		self._target = target

	@abc.abstractmethod
	def setMeasurement(self, measurement):
		raise NotImplementedError('This class must implement a way to set the reading from sensors')

	def setActualRAWRC(self, actualRAWRC: int):
		"""
		Sets the actual RAW RC sent to the channel.
		:param actualRAWRC:
		:return:
		"""
		self._actualRAWRC = actualRAWRC


	@abc.abstractmethod
	def getLock(self):
		raise NotImplementedError('This class must implement a way to lock its shared resources')

	def setUpperLimit(self, uLimit: int):
		"""
		Sets the Upper Limit of the output
		:param uLimit: the Upper Limit
		:type uLimit: int
		"""
		self._upperLimit = uLimit

	def getUpperLimit(self) -> int:
		"""
		Gets the Upper Limit of the output
		:return: the Upper Limit
		:rtype: int
		"""
		return self._upperLimit

	def setLowerLimit(self, lLimit: int):
		"""
		Sets the Lower Limit of the output
		:param lLimit: the Lower Limit
		:type lLimit: int
		"""
		self._lowerLimit = lLimit

	def getLowerLimit(self) -> int:
		"""
		Gets the Lower Limit of the output
		:return: the Lower Limit
		:rtype: int
		"""
		return self._lowerLimit

	def computePID(self) -> int:
		"""
		Computes the output value based on PID algorithm.
		:return: the output value constrained by Upper and Lower limits.
		:rtype: int
		"""
		self._error = self._target - self._measurement
		new_RAW_RC = self._actualRAWRC +\
		             (self._error * self._kP) +\
		             (self._acc_error * self._kI) +\
		             (self._previous_error * self._kD)

		self._previous_error = self._error

		if (new_RAW_RC >= self._upperLimit and self._error > 0) or (new_RAW_RC <= self._lowerLimit and self._error < 0):
			self._error = 0.0

		self._acc_error += self._error

		new_RAW_RC = max(min(self._upperLimit, new_RAW_RC), self._lowerLimit)
		self._actualRAWRC = new_RAW_RC
		return int(round(new_RAW_RC))
