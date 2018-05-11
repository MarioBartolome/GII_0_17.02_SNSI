import numpy as np


def constraintToWorldSize(coordinate_vector, world_size):
	'''
	Constraints inplace a vector of coordinates to the world size passed.

	:param coordinate_vector: A vector of coordinates.
	:param world_size: The world max length
	:rtype: None
	'''

	coordinate_vector[coordinate_vector < 0] = 0
	coordinate_vector[coordinate_vector >= world_size] = world_size


def computeDistances(segments: np.ndarray) -> np.ndarray:
	'''
	Computes the module of the segments, being a segment an init and end point.

	:param segments: arrays of init,end points
	:type segments: np.ndarray
	:return: The modules of the segments.
	:rtype: np.ndarray
	'''

	return np.linalg.norm(segments[0] - segments[1])


def getRays(particles: np.ndarray, angles: np.ndarray, world_size: np.ndarray) -> np.ndarray:
	'''
	Computes the rays having particles coordinates as origin, with the different angles for the sensors,
	keeping in mind relative heading of the particle and with a max_length of the given world size.
	http://www.disfrutalasmatematicas.com/geometria/circunferencia-unidad.html

	:param particles: Particles to work with.
	:type particles: np.ndarray
	:param angles: The angles of the different virtual sensors.
	:type angles: np.ndarray
	:param world_size: The size of the world, say *window*.
	:type world_size: np.ndarray
	:return: The end coordinates of the rays.
	:rtype: np.ndarray
	'''

	angles_number = angles.shape[1]

	return np.array([np.repeat(particles[:, 0], angles_number) +
	                 np.cos(angles.ravel()) * world_size[0],
	                 np.repeat(particles[:, 1], angles_number) +
	                 np.sin(angles.ravel()) * world_size[1]]).T.reshape(particles.shape[0], angles_number, 2)


def onCCW(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
	'''
	Determines if three points are placed on a CCW manner.

	:param A: First point.
	:param B: Second point.
	:param C: Third point.
	:return: True or False.
	'''

	return np.array((C[:, 1] - A[1]) * (B[:, 0] - A[0]) > (B[:, 1] - A[1]) * (C[:, 0] - A[0]))


def doIntersect(s1: np.ndarray, s2: np.ndarray) -> np.ndarray:
	'''
	Determines if two segments intersect.

	:param s1: First segment.
	:type s1: np.ndarray
	:param s2: Second segment.
	:type s2: np.ndarray
	:return: True or False.
	'''

	a1, a2 = s1
	b1, b2 = s2
	return (onCCW(a1, b1, b2) != onCCW(a2, b1, b2)) & (onCCW(a1, np.array([a2]), b1) != onCCW(a1, np.array([a2]), b2))


def segIntersections(rays_o: np.ndarray, rays_d: np.ndarray, obstacles: np.ndarray) -> np.ndarray:
	'''
	Determines where two segments intersect, if they do.
	It implies determine if three points are placed on CCW. If the slope between AB is smaller than AC,
	then they're CCW.
	Being s1=AB and s2=CD, they only intersect if AB are separated by CD and CD are separated by AB.
	If AB are separated by CD then ACD and BCD are placed in opposed directions.
	Therefore, either ACD or BCD are CCW but not both.

	:param rays_o: Origin segments.
	:type rays_o: np.ndarray
	:param rays_d: Destination segments.
	:type rays_d: np.ndarray
	:param obstacles: Second segments.
	:type obstacles: np.ndarray
	:return: The coordinates of the intersection, if existing.
	'''

	intersections = []

	b1, b2 = obstacles.astype(float)

	for i in range(rays_o.shape[0]):
		for j in range(rays_d.shape[1]):
			a1, a2 = rays_o[i].astype(float), rays_d[i, j].astype(float)


			da = np.atleast_2d(a2 - a1)
			db = np.atleast_2d(b2 - b1)
			dp = np.atleast_2d(a1 - b1)
			T = np.array([[0, -1], [1, 0]])
			dap = np.dot(da, T)
			denom = np.sum(dap * db, axis=1)
			num = np.sum(dap * dp, axis=1)
			intersection_points = np.atleast_2d(num / denom).T * db + b1
			inters_mask = doIntersect(np.array([a1, a2]), obstacles)

			intersections_on_range = np.zeros_like(intersection_points)
			intersections_on_range[inters_mask] = intersection_points[inters_mask]
			intersections.append(intersections_on_range)


	return np.array(intersections)


if __name__ == '__main__':

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

	sensor_number = 7
	angles = []
	for i in range(particles.shape[0]):
		angles.append(np.linspace(particles[i, 2] - np.pi / 2.0, particles[i, 2] + np.pi / 2.0, sensor_number))
	angles = np.array(angles)
	particles_rays = getRays(particles, angles, np.array([3.0, 3.0]))

	print(segIntersections(particles[:, :2], particles_rays, obstacles))
