from unittest import TestCase
from backend.algorithms.testing.test_histogramGrid import histog
from backend.algorithms.VFH import PolarHistogram
from backend.algorithms.VFH import HeadingControl
import numpy as np

polar_histog = PolarHistogram(histog)
head_control = HeadingControl(0, polar_histog)
drone_global_location = np.array([4, 2])
goal = np.array([3,2])
v_max = np.random.randint(10)

class TestHeadingControl(TestCase):
	def test_computeCandidateValleys(self):
		self.assertTrue(
			np.all(head_control.computeCandidateValleys(
				polar_histog.computePODsmoothing(
					polar_histog.computeObstacleDensity(0)
				)
			) == np.array([2, 72]))
		)

	def test_computeSpeed(self):
		self.assertTrue(head_control.computeHeading(0, goal, drone_global_location, Vmax=v_max)[1] == v_max)

	def test_computeHeading(self):
		self.assertTrue(head_control.computeHeading(0, goal, drone_global_location, Vmax=v_max)[0] == 180)
