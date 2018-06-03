from backend.yawController import YawController
from test.VFH import HistogramGrid, PolarHistogram, HeadingControl
from backend.ParticleFilter import ParticleFilter
from backend import Geometry
import numpy as np
from typing import List, Dict


class ObstacleAvoidanceWrapper:

	def __init__(
			self,
			yawC_priority: int,
			yawC_channel: List[int],
			VFH_Rmax: int,
			VFH_Rmin: int,
			VFHPF_fullMap: np.ndarray,
			PF_turn_noise: float,
			PF_forward_noise: float,
			PF_heading_coverage: int = 12,
			VFH_windowSize: int = 141,
			VFH_cellSize: int = 5,
			VFHPF_epsilon: float = 0.05,
			VFH_omega: int = 30,
			VFH_safetyThreshold: int = 2,
			VFH_MaxSpeed: int = 8
	):
		"""
		Creates an wrapper for the obstacle avoidance controller.
		It will be feeded by the VFH which is feeded by the ParticleFilter.

		:param yawC_priority: Priority of the controller.
		:type yawC_priority: int
		:param yawC_channel: Channels to control.
		:type yawC_channel: List
		:param VFH_Rmax: Maximum distance for the sensors.
		:type VFH_Rmax: int
		:param VFH_Rmin: Minimum distance for the sensors.
		:type VFH_Rmin: int
		:param VFHPF_fullMap: The map representing the area.
		:type VFHPF_fullMap: np.ndarray
		:param PF_turn_noise: Error when turning.
		:type PF_turn_noise: float
		:param PF_forward_noise: Error when moving forward.
		:type PF_forward_noise: float
		:param PF_heading_coverage: Amount of sectors to divide one cell heading. Defaults to 12.
		:type PF_heading_coverage: int
		:param VFH_windowSize: Size of the window that travels with the agent. Defaults to 141.
		:type VFH_windowSize: int
		:param VFH_cellSize: Size of the cell. Defaults to 5.
		:type VFH_cellSize: int
		:param VFHPF_epsilon: mean sonar deviation error. Defaults to 0.05
		:type VFHPF_epsilon: float
		:param VFH_omega: Beam aperture for sensors. Defaults to 30.
		:type VFH_omega: int
		:param VFH_safetyThreshold: Under which is safe to navigate a sector. Defaults to 2.
		:type VFH_safetyThreshold: int
		:param VFH_MaxSpeed: Maximum speed for the agent. Defaults to 8.
		:type VFH_MaxSpeed: int
		"""

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
		                             VFHPF_fullMap,
		                             windowSize=VFH_windowSize,
		                             cellSize=VFH_cellSize,
		                             epsilon=VFHPF_epsilon,
		                             omega=VFH_omega
		                             )
		self._polarHistog = PolarHistogram(self._histog)
		self._headingController = HeadingControl(VFH_safetyThreshold, self._polarHistog)
		self._agent_position = np.array([0, 0])
		self._goal = np.array([10, 10])
		# TODO: Maybe the PF should run on a separate thread... so it will make all its math while ctrlWrapper is busy
		# TODO: consider blocking access to sensor readings and agent_position to achieve it
		self._pf = ParticleFilter(VFHPF_fullMap, PF_turn_noise, PF_forward_noise, VFHPF_epsilon, PF_heading_coverage)
		# TODO: Make PF to compute the obstacles given the map
		self._obstacles = self._pf.computeObstacles()
		self._particles = self._pf.getParticleMap().T
		self._world_size = VFHPF_fullMap.shape
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

	def setGoal(self, goal: np.ndarray):
		"""
		Sets the goal to reach by the VFH

		:param goal: The goal to reach, as a pair of coordinates.
		:type goal: np.ndarray
		"""
		self._goal = goal

	def setMeasurement(self, measurements: List[Dict, Dict]):

		# TODO: UNDER DEVELOPMENT AND TESTING!!!
		distances = measurements[0]
		heading = measurements[1]['heading']
		self._yawController.setMeasurement(heading)

		self._histog.setSensorsMeasurements(distances)

		sensor_number = len(distances)
		angles = np.array(distances.keys())

		particles_rays = Geometry.getRays(self._particles, angles, np.array(self._world_size))

		intersections = Geometry.segIntersections(self._pf.getPositions().T, particles_rays, self._obstacles)
		particles_measurements = np.linalg.norm(
			np.repeat(self._particles[:, :2], sensor_number * self._obstacles.shape[1], axis=0).reshape(
				intersections.shape) - intersections, axis=2)

		agent_measurements = np.array(distances.keys())
		particles_probabilities = self._pf.computeProbabilities(particles_measurements, agent_measurements)

		next_gen_sample = self._pf.resample(particles_probabilities, int(self._particles.shape[0] * 0.25))
		self._agent_position = self._particles[np.argmax(particles_probabilities[next_gen_sample])]


		desired_heading, desired_speed = self._headingController.computeHeading(heading,
		                                                                        self._goal,
		                                                                        self._agent_position,
		                                                                        Vmax=self._max_speed
		                                                                        )
		self.setSpeed(desired_speed)
		self._yawController.setTarget(desired_heading)
