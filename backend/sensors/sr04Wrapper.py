
from backend.Sensor import Sensor
from typing import List, Dict, Iterable
import atexit


class sr04Wrapper:

	def __init__(self, trigger_pins, echo_pins, angles):
		self._sensors = [
			Sensor(trigger_pin, echo_pin, angle) for trigger_pin, echo_pin, angle in zip(
				trigger_pins,
				echo_pins,
				angles
			)
		]

		self._distances = {angle: None for angle in angles}
		atexit.register(self.cleanup)

	def getSensors(self) -> List[Sensor]:
		return self._sensors

	def getAnglesAndDistances(self) -> Dict:
		tmp_dst = self._distances
		return tmp_dst

	def getDistances(self) -> Iterable:
		return list(self.getAnglesAndDistances().values())

	def pollDistances(self):
		for sensor in self.getSensors():
			self.getAnglesAndDistances()[sensor.getAngle()] = sensor.getDistance()

	def cleanup(self):
		self.getSensors().pop().stop()
