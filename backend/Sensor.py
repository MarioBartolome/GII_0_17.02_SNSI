from Bluetin_Echo import Echo

class Sensor:

	def __init__(self, trigger_pin, echo_pin, angle):

		self._trigger_pin = trigger_pin
		self._echo_pin = echo_pin
		self._angle = angle
		self._sr04 = Echo(self._trigger_pin, self._echo_pin)

	def getDistance(self, samples = 1):
		return self._sr04.read('cm', samples)

	def getAngle(self):
		return self._angle

	def getTriggerPin(self):
		return self._trigger_pin

	def getEchoPin(self):
		return self._echo_pin

	def stop(self):
		self._sr04.stop()
