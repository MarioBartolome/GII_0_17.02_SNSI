"""
Author: Mario Bartolomé
Date: Feb 07, 2018
######

This file is an implementation of a Vector Field Histogram.

Due to shortcomings of Potential Fields methods (VFF), i.e the drone won't make it through a space full of close
obstacles, like a corridor, the big computational time it requires, and the lost of information during the add-up of
resulting forces, all the points are reduced to just a Force Vector (direction and magnitude of it),
a VFH has been implemented.

The VFH method uses a two-stage data reduction, instead of the just add-up on the VFF, and therefore three levels of
data representation are created:

	- Histogram Grid (**C**): Detailed description of drone's environment. A cartesian histogram grid real-time updated
	  with data taken from sensors.
	- One dimensional Polar Histogram (**H**): It comprises *n* angular sectors of width *⍺*. Each sector, *k*, holds a
	  value *hk*, that represents the Polar Obstacle Density (POD) in the direction of sector *k*.
	- Output layer of VFH: returns the values of steering angle and some other values.

"""


import numpy as np


class HistogramGrid:
	"""
	A Cartesian Histogram Grid 
	"""
	UNKNOWN_STATE = 0

	def __init__(self, sensors: list, Rmax: int, Rmin: int, Ru: int, map: np.ndarray, windowSize: int = 35, cellSize: int = 10, epsilon: float = 0.05, omega: int = 30, sense: function = None):
		"""
		Constructor method for Cartesian Histogram Grid.

		:param sensors: contains references to all the sensors to use.
		:type sensors: list
		:param Rmax: maximum distance for the sensors.
		:type Rmax: int
		:param Rmin: minimum distance for the sensors.
		:type Rmin: int
		:param Ru: measurement threshold. Under it, is considered safe to navigate.
		:type Ru: int
		:param map: The map the robot is moving on. Representing square cells.
		:type map: ndarray
		:param windowSize: Size of the, square, window that *follows* the robot.
		:type windowSize: int
		:param cellSize: Side length of each cell. The lower, the higher the accurate. Defaults to 5.
		:type cellSize: int
		:param epsilon: Optional, defaults to 0.05. Mean sonar deviation error.
		:type epsilon: float, optional
		:param omega: Optional, defaults to 30. Beam aperture in deg.
		:type omega: int
		:param sense: If defined, will be triggered to construct the Histogram Grid.
		:type sense: function

		"""
		self._sensors = sensors
		self._Rmax = Rmax
		self._Rmin = Rmin
		self._Ru = Ru
		self._map = map
		self._windowSize = windowSize
		self._cellSize = cellSize
		self._epsilon = epsilon
		self._omega = omega
		self._sense = sense
		self._distances = self.getDistances()

	def resetMap(self):
		self._map = np.zeros_like(self._map)

	def getDistances(self) -> np.ndarray:
		"""
		Will calculate the Euclidean distance from the center of the Active Window to each cell on the active window.

		:return: A matrix of distances from the center point.
		"""
		return np.linalg.norm(
			np.indices((self._windowSize, self._windowSize))
			.ravel(order='F')
			.reshape(self._windowSize ** 2, 2)
			- np.array([self._windowSize // 2, self._windowSize // 2]), axis=1
		).reshape(self._windowSize, self._windowSize)

	def getAngles(self, sensor, heading, window):
		return 0

	def getActiveRegion(self):
		return 0

	def getSampledPoints(self, sensor, heading, P) -> tuple:
		window = self.getWindow(P)
		angles = self.getAngles(sensor, heading, window)

		return 0,0

	def computeEmptyness(self, S: tuple, P: list(tuple)) -> float:
		dst = 0
		measured_dst = 0
		# Distance to the point inside the range [Rmin, R]
		if self._Rmin < dst < measured_dst - self._epsilon:
			empt_dst = 1 - ((dst - self._Rmin) / (measured_dst - self._epsilon - self._Rmin)) ** 2
		else:
			empt_dst = 0

		return empt_dst + self.angularOccupancy(S, P)

	def angularOccupancy(self, S: tuple, P: list(tuple)) -> float:

		# Angle to the point inside the range [-omega/2, omega/2]
		effective_angle = self._omega/2
		if -effective_angle < theta < effective_angle:
			return 1 - (2 * theta/self._omega) ** 2
		else:
			return 0

