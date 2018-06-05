from backend.autoControllers.altitudeController import AltitudeController
from typing import List
import time

class TakeOffLander:
	def __init__(self,
	             MAX_ALTITUDE: int,
	             priority: int,
	             channels: List[int],
	             kP: float = 0.002,
	             kI: float = 0.0,
	             kD: float = 0.00085,
	             available = False
	             ):
		"""
		This class controls the process of TakingOff or Landing.

		:param MAX_ALTITUDE: Maximum altitude to reach by the taking off controller.
		:type MAX_ALTITUDE: int
		:param priority: The priority of the controller.
		:type priority: int
		:param channels: The channels to control.
		:type channels: List
		:param kP: Proportional parameter.
		:type kP: float
		:param kI: Integral parameter.
		:type kI: float
		:param kD: Derivative parameter.
		:type kD: float
		"""
		self._altHoldController = AltitudeController(kP=kP, kI=kI, kD=kD)
		self._altH_priority = priority
		self._altH_channels = channels
		self._altHoldController.setAvailability(available)
		self._altH_checkAvMethod = self._altHoldController.isAvailable
		self._altH_getLockMethod = self._altHoldController.getLock
		self._taking_off = True
		self._landing = False
		self._actual_alt = 0
		self._MAX_ALTITUDE = MAX_ALTITUDE
		self._last_call = time.time()
		self._ready_to_fly = False

	def takeOff(self):
		"""
		Sets the altitude to achive during taking off.

		"""
		self._altHoldController.setTarget(self._MAX_ALTITUDE)
		self._taking_off = False

	def setLanding(self, land: bool):
		"""
		Sets the landing parameter.

		:param land: a boolean indicating whether to land or not.
		"""
		self._landing = land

	def land(self):
		"""
		Reduces the target of the altitude controller at 1cm/s
		:return:
		"""
		callTime = time.time()
		if callTime - self._last_call > 1:
			self._altHoldController.setTarget(max(0, self._actual_alt - 1))
			self._last_call = callTime

	def getChannels(self) -> List:
		"""
		Computes the channels keeping on mind if the system is taking off or landing.
		:return: The list of channels
		"""
		if self._taking_off:
			self.takeOff()

		if self._landing:
			self.land()

		return self._altHoldController.getChannels() + [2000]

	def setMeasurement(self, measurements):
		self._actual_alt = measurements[0]
		self._altHoldController.setMeasurement(measurements)

	def getPriority(self):
		return self._altH_priority

	def isAvailable(self):
		return self._altH_checkAvMethod()

	def getLock(self):
		return self._altH_getLockMethod()

