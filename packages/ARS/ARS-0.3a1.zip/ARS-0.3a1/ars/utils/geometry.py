import numpy as np

import ars.utils.mathematical as mut

import generic as gut


rtb_license = """RTB (The Robotics Toolbox for Matlab) is free software: you
can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


def _rot_matrix_to_rpy_angles(rot_matrix, zyx=False):
	"""The roll-pitch-yaw angles corresponding to a rotation matrix.
	The 3 angles RPY correspond to sequential rotations about the X, Y and Z
	axes respectively.

	WARNING: for the convention where Y axis points upwards, swap the returned
	pitch and yaw. The input remains the same.


	Translated to Python by German Larrain.

	Original version in Matlab, part of	'The Robotics Toolbox for Matlab (RTB)'
	as '/robot/tr2rpy.m'
	Copyright (C) 1993-2011, by Peter I. Corke. See `rtb_license`.

	"""
	m = mut.matrix_as_3x3_tuples(rot_matrix)

	# "eps: distance from 1.0 to the next largest double-precision number"
	eps = 2e-52 # http://www.mathworks.com/help/techdoc/ref/eps.html

	rpy_1 = 0.0
	rpy_2 = 0.0
	rpy_3 = 0.0

	if not zyx:
		# XYZ order
		if abs(m[2][2]) < eps and abs(m[1][2]) < eps:  # if abs(m(3,3)) < eps && abs(m(2,3)) < eps
			# singularity
			rpy_1 = 0.0
			rpy_2 = mut.atan2(m[0][2], m[2][2])  # atan2(m(1,3), m(3,3))
			rpy_3 = mut.atan2(m[1][0], m[1][1])  # atan2(m(2,1), m(2,2))
		else:
			rpy_1 = mut.atan2(-m[1][2], m[2][2])  # atan2(m(2,1), m(2,2))
			# compute sin/cos of roll angle
			sr = mut.sin(rpy_1)  # sr = sin(rpy(1))
			cr = mut.cos(rpy_1)  # cr = cos(rpy(1))
			rpy_2 = mut.atan2(m[0][2], cr * m[2][2] - sr * m[1][2])  # atan2(m(1,3), cr * m(3,3) - sr * m(2,3))
			rpy_3 = mut.atan2(-m[0][1], m[0][0])  # atan2(-m(1,2), m(1,1))
	else:
		# old ZYX order (as per Paul book)
		if abs(m[0][0]) < eps and abs(m[1][0]) < eps:  # if abs(m(1,1)) < eps && abs(m(2,1)) < eps
			# singularity
			rpy_1 = 0.0
			rpy_2 = mut.atan2(-m[2][0], m[0][0])  # atan2(-m(3,1), m(1,1))
			rpy_3 = mut.atan2(-m[1][2], m[1][1])  # atan2(-m(2,3), m(2,2))
		else:
			rpy_1 = mut.atan2(m[1][0], m[0][0])  	# atan2(m(2,1), m(1,1))
			sp = mut.sin(rpy_1)  					# sp = sin(rpy(1))
			cp = mut.cos(rpy_1)  					# cp = cos(rpy(1))
			rpy_2 = mut.atan2(-m[2][0],  			# atan2(-m(3,1),
				cp * m[0][0] + sp * m[1][0])  		# cp * m(1,1) + sp * m(2,1))
			rpy_3 = mut.atan2(sp * m[0][2] - cp * m[1][2],  # atan2(sp * m(1,3) - cp * m(2,3),
				cp * m[1][1] - sp * m[0][1])  				# cp*m(2,2) - sp*m(1,2))

	return rpy_1, rpy_2, rpy_3


class Transform:
	def __init__(self, position, rot_matrix):
		"""
		position: a 3-tuple
		rot_matrix: a 9-tuple
		"""
		if not rot_matrix:
			rot_matrix = []
			rot_matrix[0:3] = (1,0,0)
			rot_matrix[3:6] = (0,1,0)
			rot_matrix[6:9] = (0,0,1)
			rot_matrix = tuple(rot_matrix)

		row1 = rot_matrix[0:3] + (position[0],)
		row2 = rot_matrix[3:6] + (position[1],)
		row3 = rot_matrix[6:9] + (position[2],)
		row4 = (0,0,0,1)
		self.matrix = (row1,row2,row3,row4)

	def __str__(self):
		return str(self.matrix)

	def get_long_tuple(self):
		return gut.nested_iterable_to_tuple(self.matrix)

	def get_position(self):
		raise NotImplementedError()

	def get_rotation_matrix(self):
		raise NotImplementedError()


def rot_matrix_to_hom_transform(rot_matrix):
	"""From transform.r2t in Corke's Robotic Toolbox (python) rot_matrix 3x3
	matrix.	It may be a tuple, tuple of tuples or the result of numpy.mat()"""

	if isinstance(rot_matrix, tuple):
		if len(rot_matrix) == 9:
			rot_matrix = (rot_matrix[0:3], rot_matrix[3:6], rot_matrix[6:9])

	return np.concatenate( (np.concatenate((rot_matrix, np.zeros((3,1))),1),
							np.mat([0,0,0,1])) )


def calc_rotation_matrix(axis, angle):
	r"""
	Returns the row-major 3x3 rotation matrix defining a rotation around axis by
	angle.

	Formula is the same as the one presented here (as of 2011.12.01):
	http://goo.gl/RkW80

	.. math::

		R = \begin{bmatrix}
		\cos \theta +u_x^2 \left(1-\cos \theta\right) &
		u_x u_y \left(1-\cos \theta\right) - u_z \sin \theta &
		u_x u_z \left(1-\cos \theta\right) + u_y \sin \theta \\
		u_y u_x \left(1-\cos \theta\right) + u_z \sin \theta &
		\cos \theta + u_y^2\left(1-\cos \theta\right) &
		u_y u_z \left(1-\cos \theta\right) - u_x \sin \theta \\
		u_z u_x \left(1-\cos \theta\right) - u_y \sin \theta &
		u_z u_y \left(1-\cos \theta\right) + u_x \sin \theta &
		\cos \theta + u_z^2\left(1-\cos \theta\right)
		\end{bmatrix}

	The returned matrix format is length-9 tuple.

	"""

	cos_theta = mut.cos(angle)
	sin_theta = mut.sin(angle)
	t = 1.0 - cos_theta
	return (t * axis[0]**2 + cos_theta,
		t * axis[0] * axis[1] - sin_theta * axis[2],
		t * axis[0] * axis[2] + sin_theta * axis[1],
		t * axis[0] * axis[1] + sin_theta * axis[2],
		t * axis[1]**2 + cos_theta,
		t * axis[1] * axis[2] - sin_theta * axis[0],
		t * axis[0] * axis[2] - sin_theta * axis[1],
		t * axis[1] * axis[2] + sin_theta * axis[0],
		t * axis[2]**2 + cos_theta)


def make_OpenGL_matrix(rotation, position):
	"""Returns an OpenGL compatible (column-major, 4x4 homogeneous)
	transformation matrix from ODE compatible (row-major, 3x3) rotation matrix
	rotation and position vector position.

	The returned matrix format is length-9 tuple.

	"""
	return (rotation[0], rotation[3], rotation[6], 0.0,
		rotation[1], rotation[4], rotation[7], 0.0,
		rotation[2], rotation[5], rotation[8], 0.0,
		position[0], position[1], position[2], 1.0)


def get_body_relative_vector(body, vector):
	"""Returns the 3-vector vector transformed into the local coordinate system
	of ODE body 'body'"""
	return mut.rotate3(mut.transpose3(body.get_rotation()), vector)


def rot_matrix_to_euler_angles(rot_matrix):
	r"""Returns the 3-1-3 Euler angles `phi`, `theta` and `psi` (using the
	x-convention) corresponding to the rotation matrix `rot_matrix`, which
	is a tuple of three 3-element tuples, where each one is a row (what is
	called row-major order).

	Using the x-convention, the 3-1-3 Euler angles `phi`, `theta` and `psi`
	(around	the Z, X and again the Z-axis) can be obtained as follows:

	.. math::

		\phi &= \arctan2(A_{31}, A_{32}) \\
		\theta &= \arccos(A_{33}) \\
		\psi &= -\arctan2(A_{13}, A_{23})

 	http://en.wikipedia.org/wiki/Rotation_representation_(mathematics)%23Rotation_matrix_.E2.86.94_Euler_angles

	"""
	A = rot_matrix
	phi = mut.atan2(A[2][0], A[2][1])		# arctan2(A_{31}, A_{32})
	theta = mut.acos(A[2][2])				# arccos(A_{33})
	psi = -mut.atan2(A[0][2], A[1][2])		# -arctan2(A_{13}, A_{23})
	angles = (phi, theta, psi)
	return angles


def calc_inclination(rot_matrix):
	"""Returns the inclination (as `pitch` and `roll`) inherent of a rotation
	matrix ``rot_matrix``, with respect to the plane (XZ, since the	vertical
	axis is Y). `pitch` is the rotation around Z axis and `roll`
	around Y.

	Examples::

		rot_matrix = calc_rotation_matrix((1.0, 0.0, 0.0), pi/6)
		pitch, roll = gemut.calc_inclination(rot_matrix)
		pitch: 0.0, roll: pi/6

		rot_matrix = calc_rotation_matrix((0.0, 1.0, 0.0), whatever)
		pitch, roll = gemut.calc_inclination(rot_matrix)
		pitch: 0.0, roll: 0.0

		rot_matrix = calc_rotation_matrix((0.0, 0.0, 1.0), pi/6)
		pitch, roll = gemut.calc_inclination(rot_matrix)
		pitch: pi/6, roll: 0.0

	"""
	# THE FOLLOWING worked only in some cases, damn
	#y_up = mut.upAxis
	#z_front = mut.bkwdAxis
	#x_right = mut.rightAxis
	#
	#up_rotated = mut.rotate3(rot_matrix, y_up)
	#pitch_proj = mut.dot_product(mut.cross_product(y_up, up_rotated), x_right)
	#pitch =  mut.sign(pitch_proj) * mut.acos_dot3(y_up, up_rotated)
	#
	#front_rotated = mut.rotate3(rot_matrix, z_front)
	#roll_proj = mut.dot_product(mut.cross_product(z_front, front_rotated), y_up)
	#roll = mut.sign(roll_proj) * mut.acos_dot3(z_front, front_rotated)
	#
	#return pitch, roll

	roll_x, pitch_y, yaw_z = _rot_matrix_to_rpy_angles(rot_matrix)
	roll = roll_x
	pitch = yaw_z
	#yaw = pitch_y  # we don't need it
	return pitch, roll
