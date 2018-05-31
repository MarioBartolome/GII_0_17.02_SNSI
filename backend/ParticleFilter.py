'''
Author: Mario Bartolomé
Date: Apr 17, 2018
######

This file aims to provide an implementation of a Particle Filter method for localization purposes.
'''

import numpy as np


class ParticleFilter:
	def __init__(self,
	             areaMap: np.ndarray,
	             turn_noise: float,
	             forward_noise: float,
	             sense_noise: float,
	             heading_coverage: int = 12
	             ):

		self._area_map = areaMap
		#TODO MODIFY THIS TO BE ABLE TO DEFINE BEGIN AND END OF A SEGMENT REPRESENTING A BARRIER!
		#todo IT WILL TAKE LESS MEMORY, AS ONLY SEGMENTS ARE KEPT AND MAP IS GENERATED ON THE FLY
		#todo SLOWER, BUT EASIER TO USE WITH Geometry.py
		self._empty_spaces = np.where(areaMap == 0)
		self._particle_number = (self._empty_spaces[0].shape[0], heading_coverage)
		self._particle_map = self.generateParticles()
		self._turn_noise = turn_noise
		self._forward_noise = forward_noise
		self._sense_noise = sense_noise

	def getParticleNumber(self) -> tuple:
		return self._particle_number

	def getEmptySpaces(self) -> np.ndarray:
		return self._empty_spaces

	def getMap(self) -> np.ndarray:
		return self._area_map

	def getForwardNoise(self) -> float:
		return self._forward_noise

	def getTurnNoise(self) -> float:
		return self._turn_noise

	def getSenseNoise(self) -> float:
		return self._turn_noise

	def getParticleMap(self) -> np.ndarray:
		return self._particle_map

	def generateParticles(self) -> np.ndarray:
		'''
		An init method used from the constructor to create the first generation of particles.

		:return: A 3D matrix containing particle position (x,y) and heading (rad).
		:rtype: np.ndarray
		'''

		particle_number = self.getParticleNumber()
		# To avoid having -180 and +180 as both are the same:
		angles = np.linspace(-np.pi + np.pi/particle_number[1], np.pi, particle_number[1])
		particles = self.getEmptySpaces()

		particles = np.r_[
			np.repeat(particles, particle_number[1]),
			np.tile(angles, particle_number[0])
		].reshape(
			3, particle_number[0] * particle_number[1]
		)

		return particles

	def getPositions(self) -> np.ndarray:
		return self._particle_map[[0, 1]].round().astype(np.int32)

	def getOrientations(self) -> np.ndarray:
		return self._particle_map[2]

	def move(self, forward, yaw):
		'''
		Updates inplace particles coordinates making use of the input and the noise set.

		:param forward: Forward movement.
		:type forward: int
		:param yaw: Turning movement.
		:type yaw: int
		:rtype: None
		'''

		assert forward >= 0
		particle_number = self.getParticleNumber()
		particle_number = particle_number[0] * particle_number[1]
		self._particle_map[2] += yaw + np.random.normal(
			0.0, self.getTurnNoise(), particle_number
		)
		noisy_dst = forward + np.random.normal(0.0, self.getForwardNoise(), particle_number)
		self._particle_map[0] += (np.cos(self.getOrientations()) * noisy_dst)
		self._particle_map[1] += (np.sin(self.getOrientations()) * noisy_dst)

		world_shape = self.getMap().shape
		Geometry.constraintToWorldSize(self._particle_map[0], world_shape[0])
		Geometry.constraintToWorldSize(self._particle_map[1], world_shape[1])

	@staticmethod
	def computeVectorizedGaussianProb(mu: np.ndarray, sigma: float, vector: np.ndarray) -> np.ndarray:
		'''
		Computes the likelihood of the agent being at a position with *mu* measurements,
		having *vector* readings with a *sigma* measurement error.
		:param mu: The particles measurements.
		:type mu: np.ndarray
		:param sigma: The sensors measuring error.
		:type sigma: float
		:param vector: The real measurements from the agent.
		:type vector: np.ndarray
		:return: A vector of normalized probabilities.
		:rtype: np.ndarray
		'''

		probs = np.exp( -((mu - vector) ** 2) / (2 * sigma ** 2) ) / \
		       (sigma * np.sqrt(2.0 * np.pi))

		return probs / np.sum(probs)

	def computeProbabilities(self, particles_measurements: np.ndarray, agent_measurements: np.ndarray) -> np.ndarray:
		'''
		Computes the aggregated and normalized probability of multiple particle's measurements being like
		agent's measurements
		:param particles_measurements: The distances from particles to obstacles.
		:type particles_measurements: np.ndarray
		:param agent_measurements: The distances from agent to obstacles.
		:type agent_measurements: np.ndarray
		:return: A vector of particle_number probabilities.
		:rtype: np.ndarray
		'''
		probs = np.prod(
			self.computeVectorizedGaussianProb(
				particles_measurements,
				self.getSenseNoise(),
				agent_measurements), axis=1
		)
		return probs / np.sum(probs)

	def resample(self, probabilities: np.ndarray, amount: int = None) -> np.ndarray:
		'''
		Creates a new generation of *amount* particles taken from the original population with a given *probabilities*
		The resampling process works with replacement, so likely particles will appear often.

		:param particles_number: The ammount of particles available
		:param probabilities:
		:param amount:
		:return:
		'''

		if not amount:
			amount = int(probabilities.shape[0] * 0.25)
		return np.random.choice(np.arange(probabilities.shape[0]), replace=True, p=probabilities, size=amount)


if __name__ == '__main__':

	import backend.Geometry as Geometry

	pFilter = ParticleFilter(np.eye(10), 0.02, 0.02, 0.02, 2)
	particles = pFilter.getParticleMap().T
	# print(particles[:, 0].T)
	sensor_number = 5
	world_size = np.array([5.0, 5.0])
	angles = []
	for i in range(particles.shape[0]):
		angles.append(np.linspace(particles[i, 2] - np.pi/2.0, particles[i, 2] + np.pi/2.0, sensor_number))

	angles = np.array(angles)

	obstacles = np.array([
		[
			[6.0, 9.0], [3.0, 6.0], [2.0, 5.0]  # Ipoints
		], [
			[8.0, 3.0], [6.0, 7.0], [5.0, 3.0]  # Epoints
		]
	])

	particles_rays = Geometry.getRays(particles, angles, world_size)
	rays = np.array([
		particles[:2].T,
		particles_rays.T
	])

	intersections = Geometry.segIntersections(pFilter.getPositions().T, particles_rays, obstacles)
	particles_measurements = np.linalg.norm(
		np.repeat(particles[:, :2], sensor_number * obstacles.shape[1], axis=0).reshape(
			intersections.shape) - intersections, axis=2)

	#print(particles_measurements)
	agent_measurements = np.array([2.5822, 12.0415, 12.0415])
	particles_probabilities = pFilter.computeProbabilities(particles_measurements, agent_measurements)
	next_gen_sample = pFilter.resample(particles_probabilities)
	print(next_gen_sample)
