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
		self._deltas = self.computeDistances()
		self._angles = self.computeAngles()
		self._emptiness = self.resetWindow()
		self._occupiness = self.resetWindow()

	def resetWindow(self)  -> np.ndarray:
		return np.zeros((self._windowSize, self._windowSize))

	def computeDistances(self) -> np.ndarray:
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

	def computeAngles(self)  -> np.ndarray:
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

	def getWindow(self) -> np.ndarray:
		"""
		Makes a grid

		:return: A (windowSize * windowSize) matrix representing the Active window
		"""
		return np.indices(
			(self._windowSize, self._windowSize)
		)[::-1]\
			.ravel(order='F')\
			.reshape(self._windowSize ** 2, 2)

	def getAngles(self) -> np.ndarray:
		"""
		Returns the angles from the center of the Active Window to each cell on the active window over *OX*.

		:return: the angles
		"""
		return self._angles

	def getDistances(self) -> np.ndarray:
		"""
		Returns the Euclidean distance from the center of the Active Window to each cell on the active window.

		:return: the deltas
		"""
		return self._deltas

	def getSensors(self) -> list:
		"""
		Returns the sensor list.

		:return: the list of sensors
		"""
		return self._sensors

	def getEpsilon(self) -> float:
		"""
		Returns the approximate deviance of the sonar readings in number of cells.

		:return: the number of cells the sonar will misread
		"""
		return self._epsilon

	def getOmega(self) -> int:
		"""
		Returns the maximum angle covered by the sonar.

		:return: the angle
		"""
		return self._omega

	def getCellSize(self) -> int:
		"""
		Returns the cell size in cm

		:return: the cell size
		"""
		return self._cellSize

	def getWindowSize(self) -> int:
		"""
		Returns the window size in cells.

		:return: the window size
		"""
		return self._windowSize

	def getOcpWindow(self) -> np.ndarray:
		"""
		Returns the occupancy window

		:return: the occupancy window
		"""
		return self._occupiness

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
			self._occupiness += ocp_window - self._occupiness * ocp_window

		return self._occupiness

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

		tmp_empt = self.computeEmptiness(droneHeading)
		tmp_ocp = self.computeOccupancy(droneHeading)

		# Begin and End points on the fullMap to convolve the window
		tmp_begin_map = location - self._windowSize // 2
		begin_map = np.max([[0,0], tmp_begin_map], axis=0)
		tmp_end_map = location + self._windowSize // 2 + 1
		end_map = np.min([self._fullMap.shape, tmp_end_map], axis=0)

		# The start point of the window is 0,0 unless the drone is so close to the border its window overflows the Map
		begin_window = np.array([0, 0])
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

class PolarHistogram:
	def __init__(self, histogrid: HistogramGrid):
		self._histogrid = histogrid

	def computeOccupancy(self, droneHeading:int) -> np.ndarray:
		"""
		Computes the VFH simpler occupancy of an active Window. Everytime a reading comes from a sensor, only the cell
		laying at the beam's bisector and at the given distance increases its value.
		:param droneHeading:
		:return:
		"""
		ocp_window = self._histogrid.getOcpWindow()
		for sensor in self._histogrid.getSensors():
			R = sensor.getDistance() // self._histogrid.getCellSize()
			dst_indexes = (R - self._histogrid.getEpsilon() <= self._histogrid.getDistances()) &\
			              (self._histogrid.getDistances() <= R + self._histogrid.getEpsilon())

			Theta = self._histogrid.getAngles() - np.deg2rad(droneHeading) - np.deg2rad(sensor.getAngle())
			Theta[Theta >= np.pi] -= np.pi * 2
			idx = np.unravel_index(np.argmin(np.abs(Theta) + np.logical_not(dst_indexes) * 999), Theta.shape)

			ocp_window[idx] += 1

		return ocp_window

	def computeObstacleMagnitude(self, droneHeading: int, a: int = 5) -> np.ndarray:
		"""
		Computes the effect that each obstacle is creating against the robot.
		This magnitude is proportional to the distance, the closer the bigger. Also the value obtained from the readings,
		is squared, so recurring readings at the same point will increase the certainty and lower ones will be treated
		as noise.

		The values *a* and *b* are positive constants that define the influence of an obstacle, determining *a* the
		strength of that force and *b* the distance it'll begin to cause a disturbance.

		:param droneHeading: the heading of the drone.
		:type droneHeading: int
		:param a: force strength of the obstacles.
		:type a: int
		:return: A magnitude grid.
		"""

		b = a/self._histogrid.getWindowSize()
		obstacle_magnitude = self.computeOccupancy(droneHeading) ** 2 \
		       * \
		       (a - b * self._histogrid.getDistances())

		return obstacle_magnitude

	def computeObstacleDensity(self, droneHeading: int, alpha: int = 5) -> np.ndarray:
		"""
		Computes the Obstacle Density on every sector. Knowing that the Polar Histogram has an arbitrary angular
		resolution *α*, such that n = 360//α, each sector k corresponds to a discrete angle.
		The density of obstacles on that sector is the summation of every ObstacleMagnitude of that sector.

		:param droneHeading: the heading of the drone.
		:type droneHeading: int
		:param alpha: angular resolution.
		:type alpha: int
		:return: The obstacle density.
		"""

		n = 360//alpha
		sector = self._histogrid.computeAngles()
		sector[sector<0] += np.pi * 2
		sector //= np.deg2rad(alpha)
		mij = self.computeObstacleMagnitude(droneHeading)
		polar_obstacle_density = np.array([
			mij[sector == s].sum() for s in range(n)
		])

		return polar_obstacle_density

	def computePODsmoothing(self, POD: np.ndarray) -> np.ndarray:
		#TODO
		pass


if __name__ == '__main__':
	from test.Sensors import Sensors
	np.core.arrayprint._line_width = 150
	sensor = Sensors()
	histog = HistogramGrid([sensor], 375, 5, 10, np.arange(15**2, dtype=np.float16).reshape(15,15), cellSize=5, windowSize=7)
	# print(histog.computeOccupancy(-22))
	# print(histog.computeEmptiness(-22))
	#print(histog.computeMap(-12, np.array([4,4])))
	polarHistog = PolarHistogram(histog)
	print(polarHistog.computeObstacleDensity(-40))
	print("Done...")
