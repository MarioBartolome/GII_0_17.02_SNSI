from unittest import TestCase
from backend.algorithms.VFH import HistogramGrid
import numpy as np

sensor_angle = 15
sensor_measurement = 7.7
max_sensor_dst = 375
min_sensor_dst = 0
threshold = 0
window_size = 7
cell_size = 5
world_map = np.arange(15 ** 2, dtype=np.float16).reshape(15, 15)

sensor = {sensor_angle: sensor_measurement, }
histog = HistogramGrid(sensor,
                       max_sensor_dst,
                       min_sensor_dst,
                       threshold,
                       world_map,
                       cellSize=cell_size,
                       windowSize=window_size)


class TestHistogramGrid(TestCase):
	def test_resetWindow(self):
		self.assertTrue(np.all(histog.resetWindow().shape == (window_size, window_size)))
		self.assertTrue(np.all(histog.resetWindow() == 0))

	def test_getWindow(self):
		self.assertTrue(np.all(histog.getWindow().shape == (window_size**2, 2)))

	def test_getSensorsMeasurements(self):
		self.assertTrue(histog.getSensorsMeasurements() is sensor)


