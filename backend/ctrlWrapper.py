'''
Author: Mario Bartolomé
Date: Apr 3, 2018
######

Wrapper for agent controller systems
'''


from backend.MultiWiiProtocol import MSPio
from backend.RemoteControl import RemoteServer
from backend.altitudeController import AltitudeController
from backend.Sensor import Sensor
from backend.sr04Wrapper import sr04Wrapper
import numpy as np
import sys
from typing import List, Callable, Dict, AnyStr


class CtrlWrapper:

	def __init__(self, controllers: Dict = None,
				channels: List = None,
				retrieveValues: List = None,
				checkAvailability: List = None,
				getLock: List = None,
				obstacleAvoidanceSensor_triggerPins: List = None,
				obstacleAvoidanceSensor_echoPins: List = None,
				obstacleAvoidanceSensor_angles: List = None,
				altitudeSensor_triggerPin: int = None,
				altitudeSensor_echoPin: int = None,
				mspioPort: AnyStr = '/dev/ttyUSB0',
				baud_rate : int =115200):
		"""
		Constructor for the Control Wrapper.
		This class aims to provide a prioritized way to manage every existent control input.
		Once a controller is added, it will be polled to gather its values for the different channels.

		:param controllers: a dictionary containing pairs of *priority*:*object* of controllers.
		:type controllers: Dict
		:param channels: a List of lists containing the channels controlled by each controller.
		:type channels: List[List]
		:param retrieveValues: a List of methods of *controller* that will be called to get the channel values.
		:type retrieveValues: List[Callable]
		:param checkAvailability: a List of methods of *controller* that will be called to check if there's channel values.
		:type checkAvailability: List[Callable]
		:param getLock: a List of methods of *controller* that will be called to achieve a synchronized lock over the controller.
		:type getLock: List[Callable]
		"""
		self._controllers = {}

		if controllers:
			for priority, controller, chann, getterMethod, checkerMethod, lockerMethod in zip(
					controllers.keys(), controllers.values(), channels, retrieveValues, checkAvailability, getLock
			):
				self.addPrioritizedController(priority, controller, chann, getterMethod, checkerMethod, lockerMethod)

		self._mspio = MSPio(serial_port=mspioPort, baud_rate=baud_rate)

		self._dstSensors = sr04Wrapper(
			obstacleAvoidanceSensor_triggerPins,
			obstacleAvoidanceSensor_echoPins,
			obstacleAvoidanceSensor_angles
		)

		self._altSensor = Sensor(altitudeSensor_triggerPin, altitudeSensor_echoPin, 0)

	def getAltitude(self):
		return self._altSensor.getDistance()

	def getAttitude(self) -> Dict:
		return self._mspio.readAttitude()

	def getObstacleDistances(self):
		return self._dstSensors.getAnglesAndDistances()

	def getMultipleSensors(self, functions: List[Callable]):
		return (val() for val in functions)

	def getMSPio(self) -> MSPio:
		"""
		Returns the used MSPio instance
		:return: MSPio in use.
		:rtype: MSPio
		"""
		return self._mspio

	class prioritizedController:

		def __init__(self, priority: int,
					controller: object,
					channels: List,
					retrieveValues: Callable,
					checkAvailability: Callable,
					getLock: Callable,
					requiresFeedBack: bool = False,
					getFeedBack: List[Callable] = None,
					setFeedBack: Callable = None
					 ):
			"""
			Constructor for a prioritized Controller.
			A controller will overwrite its input over others if its priority is higher.

			:param priority: the priority of this controller.
			:type priority: int
			:param controller: the controller.
			:type controller: object
			:param channels: the channels this controller is setting.
			:type channels: List[int]
			:param retrieveValues: a method of *controller* that will be called to get the channel values.
			:type retrieveValues: Callable
			:param checkAvailability: a methods of *controller* that will be called to check if there's channel values.
			:type checkAvailability: Callable
			:param getLock: a method of *controller* that will be called to achieve a synchronized lock over the controller.
			:type getLock: Callable
			:param requiresFeedBack: Enables feedback control features.
			:type requiresFeedBack: bool
			:param getFeedBack: If requiresFeedBack, every function on the list will be called to get feedback from sensor.
			:type getFeedBack: List[Callable]
			:param setFeedBack: If requiresFeedBack, this method will be called to set feedback.
			:type setFeedBack: Callable
			"""

			self._priority = priority
			self._controller = controller
			self._channels = channels
			self._retrieveValues = retrieveValues
			self._checkAvailability = checkAvailability
			self._getLock = getLock
			self._values = [1000, 1500, 1500, 1500, 1000]
			self._requiresFeedBack = requiresFeedBack
			self._getFeedBack = getFeedBack
			self._setFeedBack = setFeedBack

		def getPriority(self):
			return self._priority

		def getController(self):
			return self._controller

		def getChannels(self):
			return self._channels

		def getValues(self):
			self._values = self._retrieveValues()
			assert len(self._channels) == len(self._values)
			return self._values

		def isAvailable(self):
			return self._checkAvailability()

		def getLock(self):
			return self._getLock()

		def requiresFeedBack(self):
			return self._requiresFeedBack

		def getFeedBack(self) -> List[Callable]:
			return self._getFeedBack

		def setFeedBack(self, feedBack):
			self._setFeedBack(feedBack)

	def getControllers(self) -> Dict[int, prioritizedController]:
		return self._controllers

	def addPrioritizedController(
			self,
			priority: int,
			controller: object,
			channels: List,
			retrieveValues: Callable,
			checkAvailability: Callable,
			getLock: Callable,
			requiresFeedBack: bool = False,
			getFeedBack: List[Callable] = None,
			setFeedBack: Callable = None
	):
		"""
		Adds prioritized controllers.

		:param priority: the priority of the controller.
		:type priority: int
		:param controller: the controller to add.
		:type controller: object
		:param channels: a List containing the channels the controller will manage.
		:type channels: List
		:param retrieveValues: a method of *controller* that will be called to get the channel values.
		:type retrieveValues: Callable
		:param checkAvailability: a method of *controller* that will be called to check if there's channel values.
		:type checkAvailability: Callable
		:param getLock: a method of *controller* that will be called to achieve a synchronized lock over the controller.
		:type getLock: Callable
		:param requiresFeedBack: Enables feedback control features.
		:type requiresFeedBack: bool
		:param getFeedBack: If requiresFeedBack, every function on the list will be called to get feedback from sensor.
		:type getFeedBack: List[Callable]
		:param setFeedBack: If requiresFeedBack, this method will be called to set feedback.
		:type setFeedBack: Callable

		Keep on mind that if requiresFeedBack, both feedback methods will be called **before** calling *retreiveValues*
		"""
		existing_priorities = self.getControllers().keys()
		if priority in existing_priorities:
			print("**** WARNING **** Controller \" " +
				  str(self.getControllers()[priority]) +
				  "\" with priority " + str(priority) +
				  " overwritten by \"" +
				  controller.__name__ +"\""
				  )
		self.getControllers()[priority] = self.prioritizedController(priority,
		                                                             controller,
		                                                             channels,
		                                                             retrieveValues,
		                                                             checkAvailability,
		                                                             getLock,
		                                                             requiresFeedBack,
		                                                             getFeedBack,
		                                                             setFeedBack
		                                                             )


	def computeChannels(self) -> List:
		"""
		This method returns a List of raw values for channels, based on the priority of each controller.

		:return: a List of raw values for channels in *µs*
		"""
		values = np.array([1000, 1500, 1500, 1500, 1000])
		for priority in sorted(self.getControllers().keys()):
			controller = self.getControllers()[priority] # type: self.prioritizedController
			channels = controller.getChannels()
			lock = controller.getLock()
			if lock:
				lock.acquire()
			if controller.isAvailable():
				if controller.requiresFeedBack():
					controller.setFeedBack([funct() for funct in controller.getFeedBack()])
				values[channels] = controller.getValues()
			if lock:
				lock.release()
		return list(values.tolist())

	def start(self):
		"""
		Initializes the ctrlWrapper.

		"""
		mspio = self._mspio
		if mspio.isOpen():
			while True:
				mspio.setRawRC(self.computeChannels())
		# print(mspio.readAttitude())
		else:
			print('Can not stabilise communication with the agent', file=sys.stderr)
			sys.exit(1)

if __name__ == '__main__':
	import time

	# Remote controller
	remoteController = RemoteServer()
	remoteController.start()
	altSensor_trigPin = 7
	altSensor_echoPin = 8
	dstSensors_triggerPins = [13, 9, 5, 3, 21]
	dstSensors_echoPins = [19, 10, 6, 2, 20]
	dstSensors_angles = [0, 53, 90, 127, 180]

	channels = [[0, 1, 2, 3, 4]]
	getterMethod = [remoteController.getChannels]
	availMethod = [remoteController.isManualEnabled]
	getLockMethod = [remoteController.getLock]
	controller = CtrlWrapper(
		{0: remoteController},
		channels,
		getterMethod,
		availMethod,
		getLockMethod,
		dstSensors_triggerPins,
		dstSensors_echoPins,
		dstSensors_angles,
		altSensor_trigPin,
		altSensor_echoPin
	)
	time.sleep(2)

	# Altitude controller
	altHoldController = AltitudeController()
	altH_priority = 9
	altH_channels = [0]
	altHoldController.setAvailability(True)
	altHoldController.setTarget(15)
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

	# Obstacle Avoidance controller
	# TODO: UNDER DEVELOPMENT

	controller.start()
