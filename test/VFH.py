"""
Author: Mario Bartolomé
Date: Feb 14, 2018

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

	def __init__(self, sensors: list, Rmax: int, Rmin: int, Ru: int, fullMap: np.ndarray, windowSize: int = 141, cellSize: int = 5,
	             epsilon: float = 0.5, omega: int = 30):
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
		:param fullMap: The map representing the full area.
		:type fullMap: np.ndarray
		:param windowSize: Size of the, square, window that *follows* the robot.
		:type windowSize: int
		:param cellSize: Side length of each cell in cm. The lower, the higher the accurate. Defaults to 5.
		:type cellSize: int
		:param epsilon: Optional, defaults to 0.05. Mean sonar deviation error.
		:type epsilon: float, optional
		:param omega: Optional, defaults to 30. Beam aperture in deg.
		:type omega: int

		"""
		self._sensors = sensors
		self._Rmax = Rmax//cellSize
		self._Rmin = Rmin//cellSize
		self._Ru = Ru//cellSize
		self._windowSize = windowSize
		self._cellSize = cellSize
		self._epsilon = epsilon
		self._omega = omega
		self._windowDronePos = np.array([self._windowSize//2, self._windowSize//2])
		self._fullMap = fullMap
		self._window = self.getWindow()
		self._deltas = self.getDistances()
		self._angles = self.getAngles()
		self._emptiness = self.resetWindow()
		self._ocuppiness = self.resetWindow()

	def resetWindow(self):
		return np.zeros((self._windowSize, self._windowSize))

	def getDistances(self) -> np.ndarray:
		"""
		Will calculate the Euclidean distance from the center of the Active Window to each cell on the active window.

		:return: A matrix of distances from the center point. dᵢⱼ
		"""
		return np.linalg.norm(
			self._window
			- self._windowDronePos,
			axis=1
		).reshape(
			self._windowSize, self._windowSize
		)

	def getAngles(self):
		"""
		Will calculate the angle from the center of the Active Window to each cell on the active window over *OX*.

		:return: A matrix of angles from the center point.
		"""
		_tempDst = self._window - self._windowDronePos
		return np.arctan2(
			_tempDst[:, 0], _tempDst[:, 1]
		).reshape(
			self._windowSize, self._windowSize
		)

	def getWindow(self):
		"""
		Makes a grid

		:return: A (windowSize * windowSize) matrix representing the Active window
		"""
		return np.indices(
			(self._windowSize, self._windowSize)
		)[::-1]\
			.ravel(order='F')\
			.reshape(self._windowSize ** 2, 2)

	def computeEmptiness(self, droneHeading: int) -> np.ndarray:
		"""
		Computes emptiness making use of the active window the drone is moving on and the heading.

		:param droneHeading: Heading of the drone.
		:type droneHeading: int
		:return: A Histogram Grid containing emptiness chances.
		"""

		empt_window = np.zeros_like(self._deltas)
		# Distance to the point inside the range [Rmin, R]
		for sensor in self._sensors:
			R = sensor.getDistance() / self._cellSize
			dst_indexes = np.where((self._Rmin <= self._deltas) & (self._deltas <= R - self._epsilon))
			empt_window[dst_indexes] = \
				1 - (
					(self._deltas[dst_indexes] - self._Rmin)
					/ (R - self._epsilon - self._Rmin)
			) ** 2
			empt_window *= self.angularOccupancy(droneHeading)
			self._emptiness += empt_window - self._emptiness * empt_window

		return self._emptiness

	def computeOccupancy(self, droneHeading: int) -> np.ndarray:
		"""
		Computes occupancy making use of the active window the drone is moving on and the heading.

		:param droneHeading: Heading of the drone.
		:type droneHeading: int
		:return: A Histogram Grid containing emptiness chances.
		"""

		ocp_window = np.zeros_like(self._deltas)
		for sensor in self._sensors:
			R = sensor.getDistance() / self._cellSize
			dst_indexes = np.where((R - self._epsilon <= self._deltas) & (self._deltas <= R + self._epsilon))
			ocp_window[dst_indexes] = \
				1 - (
						(self._deltas[dst_indexes] - R)
						/ self._epsilon
				) ** 2
			ocp_window *= self.angularOccupancy(droneHeading)
			norm = np.sum(ocp_window)
			norm = norm if norm != 0 else 1
			ocp_window *= (1 - self._emptiness) / norm
			self._ocuppiness += ocp_window - self._ocuppiness * ocp_window

		return self._ocuppiness

	def angularOccupancy(self, droneHeading: int) -> np.ndarray:
		"""
		Computes occupancy making use of the heading.

		:param droneHeading: Heading of the drone.
		:type droneHeading: int
		:return: A Histogram Grid containing vicinity to the center of the beam chances.
		"""

		ang_window = np.zeros_like(self._angles)
		# Angle to the point inside the range [-omega/2, omega/2]
		for sensor in self._sensors:
			Theta = self._angles - np.deg2rad(droneHeading) - np.deg2rad(sensor.getAngle())
			Theta[Theta >= np.pi] -= np.pi * 2
			effective_angle = np.deg2rad(self._omega/2.0)
			ang_indexes = np.where((-effective_angle < Theta) & (Theta < effective_angle))
			ang_window[ang_indexes] += 1 - (2 * Theta[ang_indexes] / self._omega) ** 2

		return ang_window

	def computeMap(self, droneHeading: int, location: np.ndarray) -> np.ndarray:
		"""
		Computes the full Histogram Grid, making use of the active window, given by the drone's **location**

		:param droneHeading: Heading of the drone.
		:type droneHeading: int
		:param location: The location of the drone on the Histogram Grid.
		:type location: np.ndarray
		:return: An numpy ndArray matrix representing the whole Histogram Grid.
		"""

		tmp_ocp = self.computeOccupancy(droneHeading)
		tmp_empt = self.computeEmptiness(droneHeading)

		# Begin and End points on the fullMap to convolve the window
		tmp_begin_map = location - self._windowSize // 2
		begin_map = np.max([[0,0], tmp_begin_map], axis=0)
		tmp_end_map = location + self._windowSize // 2 + 1
		end_map = np.min([self._fullMap.shape, tmp_end_map], axis=0)

		# The start point of the window is 0,0 unless the drone is so close to the border its window overflows the Map
		begin_window = np.array([0,0])
		neg_idx = tmp_begin_map < 0
		if np.any(neg_idx):
			begin_window[neg_idx] = np.abs(tmp_begin_map[neg_idx])

		# The window's endpoint is windowSize unless the drone is so close to the border its window overflows the Map
		end_window = np.array([self._windowSize, self._windowSize])
		over_idx = tmp_end_map > end_map
		if np.any(over_idx):
			end_window[over_idx] -= tmp_end_map[over_idx] - self._fullMap.shape[0]

		# Finally the area of the map to be replaced by the computed occupancy/emptiness windows sits between begin_map
		#  and end_map
		ocp_idx = tmp_ocp[begin_window[0]:end_window[0], begin_window[1]:end_window[1]] >= \
		          tmp_empt[begin_window[0]:end_window[0], begin_window[1]:end_window[1]]

		self._fullMap[begin_map[0]:end_map[0], begin_map[1]:end_map[1]][ocp_idx] = \
			tmp_ocp[begin_window[0]:end_window[0], begin_window[1]:end_window[1]][ocp_idx]

		self._fullMap[begin_map[0]:end_map[0], begin_map[1]:end_map[1]][np.logical_not(ocp_idx)] = \
			-tmp_empt[begin_window[0]:end_window[0], begin_window[1]:end_window[1]][np.logical_not(ocp_idx)]

		return self._fullMap


if __name__ == '__main__':
	from Sensors import Sensors
	np.core.arrayprint._line_width = 150
	sensor = Sensors()
	histog = HistogramGrid([sensor], 375, 5, 10, np.arange(11**2).reshape(11,11), cellSize=5, windowSize=7)
	# print(histog.computeOccupancy(12))
	# print(histog.computeEmptiness(12))
	print(histog.computeMap(-180, np.array([3,2])))
	print("Done...")
