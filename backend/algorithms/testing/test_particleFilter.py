from unittest import TestCase
from backend.algorithms.ParticleFilter import ParticleFilter
import numpy as np


diag_size = 10
world_map = np.eye(diag_size)
heading_coverage = 2

pFilter = ParticleFilter(world_map, 0.02, 0.02, 0.02, heading_coverage)

class TestParticleFilter(TestCase):
	def test_getParticleNumber(self):
		self.assertTrue(np.all(pFilter.getParticleNumber() == (diag_size **2 - diag_size, heading_coverage)))

	def test_getEmptySpaces(self):
		self.assertTrue(np.all(pFilter.getEmptySpaces()[0] == np.where(world_map == 0)[0]))

	def test_generateParticles(self):
		self.assertTrue(np.all(pFilter.generateParticles().shape == (3, (diag_size**2 - diag_size) * heading_coverage)))

