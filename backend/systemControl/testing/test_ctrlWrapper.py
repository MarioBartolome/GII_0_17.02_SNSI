from unittest import TestCase
from backend.systemControl.ctrlWrapper import CtrlWrapper
from backend.autoControllers.takeOffLanding import TakeOffLander


class TestCtrlWrapper(TestCase):
	def test_getAltitude(self):
		self.assertAlmostEqual(controller.getAltitude(), 12.0, delta=1.0)


	def test_getAttitude(self):
		self.assertTrue(all(key in ['x', 'y', 'heading', 'timestamp'] for key in controller.getAttitude().keys()))


altSensor_trigPin = 7
altSensor_echoPin = 8
dstSensors_triggerPins = [13, 9, 5, 3, 21]
dstSensors_echoPins = [19, 10, 6, 2, 20]
dstSensors_angles = [0, 53, 90, 127, 180]
MAX_ALTITUDE = 80
MAX_INCLINATION = 8


controller = CtrlWrapper({}, altitudeSensor_echoPin=altSensor_echoPin, altitudeSensor_triggerPin=altSensor_trigPin)

# Altitude controller

altH_priority = 9
altH_channels = [0, 4]
altHoldController = TakeOffLander(MAX_ALTITUDE, altH_priority, altH_channels)
altH_checkAvMethod = altHoldController.isAvailable
altH_getLockMethod = altHoldController.getLock
altH_retrieveFBMethod = [controller.getAltitude]
altH_setFBMethod = altHoldController.setMeasurement
altH_getterMethod = altHoldController.getChannels
controller.addPrioritizedController(
	altH_priority,
	altHoldController,
	altH_channels,
	altH_getterMethod,
	altH_checkAvMethod,
	altH_getLockMethod,
	requiresFeedBack=True,
	getFeedBack=altH_retrieveFBMethod,
	setFeedBack=altH_setFBMethod
	)