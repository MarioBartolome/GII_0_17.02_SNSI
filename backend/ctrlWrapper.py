'''
Author: Mario Bartolomé
Date: Apr 3, 2018
######

Wrapper for agent controller systems
'''


from backend.MultiWiiProtocol import MSPio
from backend.RemoteControl import RemoteServer
import numpy as np
import sys

class CtrlWrapper:

	def __init__(self, controllers: dict = None,
	             channels: list = None,
	             retrieveValues: list = None,
	             checkAvailability: list = None,
	             getLock: list = None):
		"""
		Constructor for the Control Wrapper.
		This class aims to provide a prioritized way to manage every existent control input.
		Once a controller is added, it will be polled to gather its values for the different channels.

		:param controllers: a dictionary containing pairs of *priority*:*object* of controllers.
		:type controllers: dict
		:param channels: a list of lists containing the channels controlled by each controller.
		:type channels: list[list]
		:param retrieveValues: a list of methods of *controller* that will be called to get the channel values.
		:type retrieveValues: list[callable]
		:param checkAvailability: a list of methods of *controller* that will be called to check if there's channel values.
		:type checkAvailability: list[callable]
		:param getLock: a list of methods of *controller* that will be called to achieve a synchronized lock over the controller.
		:type getLock: list[callable]
		"""
		self._controllers = {}

		if controllers:
			for priority, controller, chann, getterMethod, checkerMethod, lockerMethod in zip(
					controllers.keys(), controllers.values(), channels, retrieveValues, checkAvailability, getLock
			):
				self.addPrioritizedController(priority, controller, chann, getterMethod, checkerMethod, lockerMethod)

		self._mspio = MSPio()


	class prioritizedController:

		def __init__(self, priority: int,
		             controller: object,
		             channels: list,
		             retrieveValues: callable,
		             checkAvailability: callable,
		             getLock: callable
		             ):
			"""
			Constructor for a prioritized Controller.
			A controller will overwrite its input over others if its priority is higher.

			:param priority: the priority of this controller.
			:type priority: int
			:param controller: the controller.
			:type controller: object
			:param channels: the channels this controller is setting.
			:type channels: list[int]
			:param retrieveValues: a method of *controller* that will be called to get the channel values.
			:type retrieveValues: callable
			:param checkAvailability: a methods of *controller* that will be called to check if there's channel values.
			:type checkAvailability: callable
			:param getLock: a method of *controller* that will be called to achieve a synchronized lock over the controller.
			:type getLock: callable
			"""

			self._priority = priority
			self._controller = controller
			self._channels = channels
			self._retrieveValues = retrieveValues
			self._checkAvailability = checkAvailability
			self._getLock = getLock
			self._values = [1000, 1500, 1500, 1500, 1000]

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

	def getControllers(self):
		return self._controllers


	def addPrioritizedController(self, priority: int,
	                             controller: callable,
	                             channels: list,
	                             retrieveValues: callable,
	                             checkAvailability: callable,
	                             getLock: callable):
		"""
		Adds prioritized controllers.

		:param priority: the priority of the controller.
		:type priority: int
		:param controller: the controller to add.
		:type controller: callable
		:param channels: a list containing the channels the controller will manage.
		:type channels: list
		:param retrieveValues: a method of *controller* that will be called to get the channel values.
		:type retrieveValues: callable
		:param checkAvailability: a method of *controller* that will be called to check if there's channel values.
		:type checkAvailability: callable
		:param getLock: a method of *controller* that will be called to achieve a synchronized lock over the controller.
		:type getLock: callable
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
		                                                             getLock)


	def computeChannels(self) -> list:
		"""
		This method returns a list of raw values for channels, based on the priority of each controller.

		:return: a list of raw values for channels in *µs*
		"""
		values = np.array([1000, 1500, 1500, 1500, 1000])
		for priority in sorted(self.getControllers().keys()):
			controller = self.getControllers()[priority] # type: self.prioritizedController
			channels = controller.getChannels()
			controller.getLock().acquire()
			if controller.isAvailable():
				values[channels] = controller.getValues()
			controller.getLock().release()
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
	remoteController = RemoteServer()
	remoteController.start()

	channels = [[0, 1, 2, 3, 4]]
	getterMethod = [remoteController.getChannels]
	availMethod = [remoteController.isManualEnabled]
	getLockMethod = [remoteController.getLock]
	controller = CtrlWrapper({0: remoteController}, channels, getterMethod, availMethod, getLockMethod)
	time.sleep(3)
	controller.start()
