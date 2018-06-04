'''
Author: Mario Bartolomé
Date: Jan 16, 2018
######

This file aims to provide a simple class to create a Potential Field.
'''
import matplotlib
matplotlib.use('MacOsX')
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import distance
import warnings
warnings.warn("The PotentialField module is deprecated. Please, use VFH for improved obstacle avoidance",
              category=DeprecationWarning, stacklevel=2)

class PotentialField:

	def __init__(self):
		"""
		Constructor method for the PotentialField algorithm

		:param obstacles: a list of tuples containing the coordinates of the obstacles
		"""

	@staticmethod
	def Uattr(r_pos, goal, epsilon=0.0625, exp=2):
		"""
		Attractive potential function.
		:param r_pos: a tuple containing the coordinates of the robot.
		:param goal: a tuple containing the coordinates of the goal point.
		:param epsilon: a positive scaling factor. Defaults to 1/16. Influence of the p.f on the speed of the robot.
		:param exp: the exponential factor of the distance function.
			Defaults to 2. As far as the robot gets from the goal, attraction increases, as closes, attraction reduces.
			Set it to 1 to achieve linear attraction to goal.
		:return: The attraction value
		"""
		return epsilon * np.linalg.norm(r_pos - goal) ** exp


	@staticmethod
	def Urep(r_pos, obstacle, eta=5, rho=1):
		"""
		Repulsive potential function.
		:param r_pos: a tuple containing the coordinates of the robot.
		:param obstacle: a tuple containing the coordinates of the obstacle point.
		:param eta: a positive scaling factor. Defaults to 1/16. Defines how hard the robot is being pushed away.
		:param rho: a positive constant. Defaults to 1. Sets the distance of influence. The higher the longer the distance
		the robot will feel the repulsive force
		:return: The repulsion value
		"""

		dst = np.linalg.norm(r_pos - obstacle)
		if dst > rho:
			return 0
		elif dst != 0:
				return eta * ((1/dst) - (1/rho))**2
		else:
			return 90

	def Upot(self, r_pos, lspace, goal, obstacles, epsilon=0.0625, eta=5, exp=2, rho=5):
		"""
		Computes the potential of the robot with the given obstacles.

		:param lspace: a space containing the plane to compute the potential field.
		:param goal: a tuple containing the coordinates of the goal point.
		:param epsilon: a positive scaling factor. Defaults to 1/16. Influence of the p.f on the speed of the robot.
		:param exp: the exponential factor of the distance function.
			Defaults to 2. As far as the robot gets from the goal, attraction increases, as closes, attraction reduces.
			Set it to 1 to achieve linear attraction to goal.
		:param eta: a positive scaling factor. Defaults to 1/16. Defines how hard the robot is being pushed away.
		:param rho: a positive constant. Defaults to 1. Sets the distance of influence. The higher the longer the distance the robot will feel the repulsive force

		:return: a tuple of u_attr: The complete potential field from goal to every point in the lspace
							u_rep:  The complete potential field from robot to every point in the lspace using obstacles
		"""

		u_attr = epsilon * np.linalg.norm(goal - lspace, axis=1) ** exp

		dst_rep = np.linalg.norm(r_pos - obstacles, axis=1)
		u_rep = eta * ((1/dst_rep) - (1/rho))**2
		u_rep[np.where(dst_rep > rho)] = 0.

		return u_attr, u_rep


potField = PotentialField()
plot = plt.figure()
ax = plot.add_subplot(111, projection='3d')
X = Y = np.arange(-20.0, 20.0, 1)
XY = np.array([[x,y] for x in X for y in Y])
goal = np.array([0,0])
r_pos = np.array([10,12])


X, Y = np.meshgrid(X, Y)
obstacles = np.array([[3, 2], [5,5], [9, 12], [10, 11]])
U_attr, U_rep = potField.Upot(r_pos, XY, goal, obstacles)

U_attr = U_attr.reshape([X.shape[0], Y.shape[0]])

# add a near obstacle to see its action against the robot...
i = 0
for obstacle in obstacles:
	U_attr[obstacle[0] + 20, obstacle[1] + 20] += U_rep[i]
	i += 1

ax.plot_wireframe(X, Y, U_attr, rstride=1, cstride=1)
ax.plot([r_pos[0]], [r_pos[1]], potField.Uattr(r_pos, goal), 'rX')
ax.plot([0], [0], [0], 'b*')
plt.show()
