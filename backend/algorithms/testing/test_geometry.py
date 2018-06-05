from unittest import TestCase
from backend.algorithms import Geometry
import numpy as np

obstacles = np.array([
		[
			[6.0, 9.0], [3.0, 6.0], [2.0, 5.0]  # Ipoints
		], [
			[8.0, 3.0], [6.0, 7.0], [5.0, 3.0]  # Epoints
		]
	])

drone_heading = np.pi / 2.0

particles = np.array(
	[
		[5.0, 4.0, np.deg2rad(90)],
		[5.0, 0.0, np.deg2rad(90)],
	]
)

sensor_number = 2
angles = []
for i in range(particles.shape[0]):
	angles.append(np.linspace(particles[i, 2] - np.pi / 2.0, particles[i, 2] + np.pi / 2.0, sensor_number))
angles = np.array(angles)

class TestGeometry(TestCase):

	def test_computeDistances(self):
		self.assertAlmostEqual(Geometry.computeDistances(np.array([[0, 0], [1, 1]])), 1.41421356)

	def test_getRays(self):
		self.assertTrue(np.allclose(
			Geometry.getRays(
				particles, angles,
				np.array([3.0, 3.0])),
			np.array([
				[[8.0, 4.0], [2.0, 4.0]],
				[[8.0, 0.0], [2.0, 0.0]]
			])
		))

	def test_segIntersections(self):
		self.assertTrue(np.allclose(
			Geometry.segIntersections(
				particles[:, :2],
				Geometry.getRays(
					particles, angles,
					np.array([3.0, 3.0])
				), obstacles),
				np.array([
					[[7.66666667, 4.0], [0.0, 0.0], [0.0, 0.0]],
					[[0.0, 0.0], [0.0, 0.0], [3.5, 4.0]],
					[[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
					[[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
				])
			)
		)


