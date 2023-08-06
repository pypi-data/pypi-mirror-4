import numpy as np

from . import mathematical as mut


rtb_license = """RTB (The Robotics Toolbox for Matlab) is free software: you
can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


def _rot_matrix_to_rpy_angles(rot, zyx=False):
	"""The roll-pitch-yaw angles corresponding to a rotation matrix.

	The 3 angles RPY correspond to sequential rotations about the X, Y and Z
	axes respectively.

	WARNING: for the convention where Y axis points upwards, swap the returned
	pitch and yaw. The input remains the same.


	Translated to Python by German Larrain.

	Original version in Matlab, part of 'The Robotics Toolbox for Matlab (RTB)'
	as '/robot/tr2rpy.m'
	Copyright (C) 1993-2011, by Peter I. Corke. See `rtb_license`.

	"""
	m = mut.matrix_as_3x3_tuples(rot)

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

	r"""An homogeneous transform.

	It is a composition of rotation and translation. Mathematically it can be
	expressed as

	.. math::

		\left[
		\begin{array}{ccc|c}
			 &  &  &  \\
			 & R &  & T \\
			 & &  &  \\
			\hline
			0 & 0 & 0 & 1
		  \end{array}
		\right]

	where `R` is the 3x3 submatrix describing rotation and `T` is the
	3x1 submatrix describing translation.

	source:
	http://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters#Denavit-Hartenberg_matrix

	"""

	def __init__(self, pos=None, rot=None):
		"""Constructor.

		With empty arguments it's just a 4x4 identity matrix.

		:param pos: a size 3 vector, or 3x1 or 1x3 matrix
		:type pos: tuple, :class:`numpy.ndarray` or None
		:param rot: 3x3 or 9x1 rotation matrix
		:type rot: tuple, :class:`numpy.ndarray` or None

		"""
		if pos is None:
			pos = (0, 0, 0)
		pos = np.array(pos)

		if pos.shape != (3, 1):
			pos = pos.reshape((3, 1))

		if rot is None:
			rot = np.identity(3)
		else:
			rot = np.array(rot)

		if rot.shape != (3, 3):
			rot = rot.reshape((3, 3))

		temp = np.hstack((rot, pos))
		self._matrix = np.vstack((temp, np.array([0, 0, 0, 1])))


	def __str__(self):
		return str(self._matrix)

	@property
	def matrix(self):
		r"""Return matrix that contains the transform values.

		:return: 4x4 matrix
		:rtype: :class:`numpy.ndarray`

		"""
		return self._matrix

	def get_long_tuple(self):
		return tuple(self._matrix.flatten())

	def get_translation(self, as_numpy=False):
		"""Get the translation component (vector).

		:param as_numpy: whether to return a numpy object or a tuple
		:return: 3-sequence
		:rtype: tuple or :class:`numpy.ndarray`

		"""
		rot = self._matrix[0:3,3]
		if as_numpy:
			return rot
		return tuple(rot)

	def get_rotation(self, as_numpy=False):
		"""Get the rotation component (matrix).

		:param as_numpy: whether to return a numpy object or a tuple
		:return: 3x3 rotation matrix
		:rtype: tuple of tuples or :class:`numpy.ndarray`

		"""
		rot = self._matrix[0:3,0:3]
		if as_numpy:
			return rot
		return mut.np_matrix_to_tuple(rot)


def rot_matrix_to_hom_transform(rot):
	"""Convert a rotation matrix to a homogeneous transform.

	source: transform.r2t in Corke's Robotic Toolbox (python)
	
	:param rot: 3x3 rotation matrix
	:type rot: a tuple, a tuple of tuples or :class:`numpy.ndarray`

	"""
	if isinstance(rot, tuple):
		if len(rot) == 9:
			rot = (rot[0:3], rot[3:6], rot[6:9])

	return np.concatenate((np.concatenate((rot, np.zeros((3, 1))), 1),
							np.mat([0, 0, 0, 1])))


def calc_rotation_matrix(axis, angle):
	r"""Return the row-major 3x3 rotation matrix defining a rotation of
	magnitude ``angle`` around ``axis``.

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


def make_OpenGL_matrix(rot, pos):
	"""Return an OpenGL compatible (column-major, 4x4 homogeneous)
	transformation matrix from ODE compatible (row-major, 3x3) rotation matrix
	rotation and position vector position.

	The returned matrix format is length-9 tuple.

	"""
	return (rot[0], rot[3], rot[6], 0.0,
		rot[1], rot[4], rot[7], 0.0,
		rot[2], rot[5], rot[8], 0.0,
		pos[0], pos[1], pos[2], 1.0)


def get_body_relative_vector(body, vector):
	"""Return the 3-vector vector transformed into the local coordinate system
	of ODE body 'body'"""
	return mut.rotate3(mut.transpose3(body.get_rotation()), vector)


def rot_matrix_to_euler_angles(rot):
	r"""Return the 3-1-3 Euler angles `phi`, `theta` and `psi` (using the
	x-convention) corresponding to the rotation matrix `rot`, which
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
	A = rot
	phi = mut.atan2(A[2][0], A[2][1])		# arctan2(A_{31}, A_{32})
	theta = mut.acos(A[2][2])				# arccos(A_{33})
	psi = -mut.atan2(A[0][2], A[1][2])		# -arctan2(A_{13}, A_{23})
	angles = (phi, theta, psi)
	return angles


def calc_inclination(rot):
	"""Return the inclination (as ``pitch`` and ``roll``) inherent of rotation
	matrix ``rot``, with respect to the plane (`XZ`, since the vertical
	axis is `Y`). ``pitch`` is the rotation around `Z` and ``roll`` around `Y`.

	Examples:

	>>> rot = calc_rotation_matrix((1.0, 0.0, 0.0), pi/6)
	>>> pitch, roll = gemut.calc_inclination(rot)
	0.0, pi/6

	>>> rot = calc_rotation_matrix((0.0, 1.0, 0.0), whatever)
	>>> pitch, roll = gemut.calc_inclination(rot)
	0.0, 0.0

	>>> rot = calc_rotation_matrix((0.0, 0.0, 1.0), pi/6)
	>>> pitch, roll = gemut.calc_inclination(rot)
	pi/6, 0.0

	"""
	# THE FOLLOWING worked only in some cases, damn
	#y_up = mut.upAxis
	#z_front = mut.bkwdAxis
	#x_right = mut.rightAxis
	#
	#up_rotated = mut.rotate3(rot, y_up)
	#pitch_proj = mut.dot_product(mut.cross_product(y_up, up_rotated), x_right)
	#pitch =  mut.sign(pitch_proj) * mut.acos_dot3(y_up, up_rotated)
	#
	#front_rotated = mut.rotate3(rot, z_front)
	#roll_proj = mut.dot_product(mut.cross_product(z_front, front_rotated), y_up)
	#roll = mut.sign(roll_proj) * mut.acos_dot3(z_front, front_rotated)
	#
	#return pitch, roll

	roll_x, pitch_y, yaw_z = _rot_matrix_to_rpy_angles(rot)
	roll = roll_x
	pitch = yaw_z
	#yaw = pitch_y  # we don't need it
	return pitch, roll


def calc_compass_angle(rot):
	"""Return the angle around the vertical axis with respect to the `X+` axis,
	i.e. the angular orientation inherent of a rotation matrix ``rot``,
	constrained to the plane aligned with the horizon (`XZ`, since the vertical
	axis is `Y`).

	"""
	roll_x, pitch_y, yaw_z = _rot_matrix_to_rpy_angles(rot)
	yaw = pitch_y
	return yaw
