from backend.yawController import YawController
from test.VFH import HistogramGrid, PolarHistogram, HeadingControl
from backend.ParticleFilter import ParticleFilter
import numpy as np
from typing import List, Dict


class ObstacleAvoidanceWrapper:

	def __init__(
			self,
			yawC_priority: int,
			yawC_channel: List[int],
			VFH_Rmax: int,
			VFH_Rmin: int,
			VFH_fullMap: np.ndarray,
			VFH_windowSize: int = 141,
			VFH_cellSize: int = 5,
			VFH_epsilon: float = 0.5,
			VFH_omega: int = 30,
			VFH_safetyThreshold: int = 2,
			VFH_MaxSpeed: int = 8
	):

		self._yawController = YawController()
		self._yawC_priority = yawC_priority
		self._yawC_channels = yawC_channel
		self._yawC_checkAvMethod = self._yawController.isAvailable
		self._yawC_getLockMethod = self._yawController.getLock
		self._yawC_setFBMethod = self._yawController.setMeasurement
		self._yawC_getterMethod = self._yawController.getChannels

		self._histog = HistogramGrid({},
		                             VFH_Rmax,
		                             VFH_Rmin,
		                             VFH_safetyThreshold,
		                             VFH_fullMap,
		                             windowSize=VFH_windowSize,
		                             cellSize=VFH_cellSize,
		                             epsilon=VFH_epsilon,
		                             omega=VFH_omega
		                             )
		self._polarHistog = PolarHistogram(self._histog)
		self._headingController = HeadingControl(VFH_safetyThreshold, self._polarHistog)
		self._agent_position = np.array([0, 0])
		self._goal = np.array([10, 10])
		# TODO: Maybe the PF should run on a separate thread... so it will make all its math while ctrlWrapper is busy
		# TODO: consider blocking access to sensor readings and agent_position to achieve it
		# self._pf = ParticleFilter()
		self._speed = 0
		self._max_speed = VFH_MaxSpeed

	def getPriority(self):
		return self._yawC_priority

	def getChannels(self):
		return self._yawC_channels

	def getLockMethod(self):
		return self._yawC_getLockMethod

	def isAvailableMethod(self):
		return self._yawC_checkAvMethod

	def getSpeed(self):
		return self._speed

	def setSpeed(self, speed):
		self._speed = speed

	def getPosition(self):
		return self._agent_position

	def setPosition(self, position):
		self._agent_position = position

	def getGoal(self):
		return self._goal

	def setGoal(self, goal):
		self._goal = goal

	def setMeasurement(self, measurements: List[Dict, Dict]):
		distances = measurements[0]
		heading = measurements[1]['heading']
		self._yawController.setMeasurement(heading)

		self._histog.setSensorsMeasurements(distances)

		desired_heading, desired_speed = self._headingController.computeHeading(heading,
		                                                                        self._goal,
		                                                                        self._agent_position,
		                                                                        Vmax=self._max_speed
		                                                                        )
		self.setSpeed(desired_speed)
		self._yawController.setTarget(desired_heading)
