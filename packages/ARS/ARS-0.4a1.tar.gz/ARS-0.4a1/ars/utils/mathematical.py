"""
Functions to perform operations over vectors and matrices;
deal with homogeneous transforms; convert angles and other structures.
"""

import itertools
from math import sqrt, pi, cos, sin, acos, atan, atan2, degrees, radians
import operator

import numpy as np

from . import generic as gut

# TODO:	attribute the code sections that were taken from somewhere else

#==============================================================================
# rotation directions are named by the third (z-axis) row of the 3x3 matrix,
# because ODE capsules are oriented along the Z-axis.
#==============================================================================

rightRot = (0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0)
leftRot = (0.0, 0.0, 1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0)
upRot = (1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0)
downRot = (1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0)
bkwdRot = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

X_AXIS = (1.0, 0.0, 0.0)
X_AXIS_NEG = (-1.0, 0.0, 0.0)
Y_AXIS = (0.0, 1.0, 0.0)
Y_AXIS_NEG = (0.0, -1.0, 0.0)
Z_AXIS = (0.0, 0.0, 1.0)
Z_AXIS_NEG = (0.0, 0.0, -1.0)

# axes used to determine constrained joint rotations
rightAxis = X_AXIS
leftAxis = X_AXIS_NEG
upAxis = Y_AXIS
downAxis = Y_AXIS_NEG
bkwdAxis = Z_AXIS  # direction: out of the screen
fwdAxis = Z_AXIS_NEG  # direction: into the screen

#==============================================================================
# added to the original refactored code
#==============================================================================


def radians_to_degrees(radians_):
	return degrees(radians_)


# TODO: combine with the corresponding scalar-argument function
def vec3_radians_to_degrees(vector_):
	result = []
	for radians_ in vector_:
		result.append(radians_to_degrees(radians_))
	return tuple(result)


def degrees_to_radians(degrees_):
	return radians(degrees_)


# TODO: combine with the corresponding scalar-argument function
def vec3_degrees_to_radians(vector_):
	result = []
	for degrees_ in vector_:
		result.append(degrees_to_radians(degrees_))
	return tuple(result)


def np_matrix_to_tuple(array_):
	"""Convert Numpy 2D array (i.e. matrix) to a tuple of tuples.

	source: http://stackoverflow.com/a/10016379/556413

	Example:
	
	>>> arr = numpy.array(((2, 2), (2, -2)))
	>>> np_matrix_to_tuple(arr)
	((2, 2), (2, -2))

	:param array_: 2D array (i.e. matrix)
	:type array_: :class:`numpy.ndarray`
	:return: matrix as tuple of tuples

	"""
	return tuple(tuple(x) for x in array_)


def matrix_multiply(matrix1, matrix2):
	"""Return the matrix multiplication of ``matrix1`` and ``matrix2``.

	:param matrix1: LxM matrix
	:param matrix2: MxN matrix
	:return: LxN matrix, product of ``matrix1`` and ``matrix2``
	:rtype: tuple of tuples

	"""
	# TODO: check objects are valid, or use exceptions to catch errors raised
	# by numpy

	a1 = np.array(matrix1)
	a2 = np.array(matrix2)
	result = np.dot(a1, a2)

	if result.ndim == 1:
		return tuple(result)
	else:
		return np_matrix_to_tuple(result)


def matrix_as_tuple(matrix_):
	"""Convert ``matrix_`` to a tuple.

	Example:

	>>> matrix_as_tuple(((1, 2), (3, 4)))
	(1, 2, 3, 4)

	:param matrix_: nested tuples
	:type matrix_: tuple
	:return: ``matrix_`` flattened as a tuple
	:rtype: tuple

	"""
	#TODO: improve a lot
	return gut.nested_iterable_to_tuple(matrix_)


def matrix_as_3x3_tuples(tuple_9):
	"""Return ``tuple_9`` as a 3-tuple of 3-tuples.

	:param tuple_9: tuple of 9 elements
	:return: ``tuple_9`` formatted as tuple of tuples

	"""
	#TODO: convert it to handle square matrices of any size

	matrix = None
	if isinstance(tuple_9, tuple):
		if len(tuple_9) == 9:
			matrix = (tuple_9[0:3], tuple_9[3:6], tuple_9[6:9])
	return matrix


def calc_acceleration(time_step, vel0, vel1):
	"""Calculate the vectorial substraction ``vel1 - vel0`` divided by
	``time step``. If any of the vectors is ``None``, then ``None`` is returned.

	``vel1`` is the velocity measured ``time_step`` seconds after ``vel0``.

	"""
	if vel0 is None or vel1 is None:
		return None
	vel_diff = sub3(vel1, vel0)
	return div_by_scalar3(vel_diff, time_step)


def vector_matrix_vector(vector_, matrix_):
	r"""Return the product of ``vector_`` transposed, ``matrix_`` and
	``vector`` again, which is a scalar value.

	.. math::
		v^\top \mathbf{M} v

	"""
	return np.dot(np.dot(np.array(vector_).T, np.array(matrix_)),
		np.array(vector_))

#==============================================================================
# Original code but formatted and some refactor
#==============================================================================


def sign(x):
	"""Return ``1.0`` if ``x`` is positive, ``-1.0`` otherwise."""
	if x > 0.0:
		return 1.0
	else:
		return -1.0


def length2(vector):
	"""Return the length of a 2-dimension ``vector``."""
	return sqrt(vector[0] ** 2 + vector[1] ** 2)


def length3(vector):
	"""Return the length of a 3-dimension ``vector``."""
	#TODO: convert it so it can handle vector of any dimension
	return sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)


def neg3(vector):
	"""Return the negation of 3-dimension ``vector``."""
	#TODO: convert it so it can handle vector of any dimension
	return (-vector[0], -vector[1], -vector[2])


def add3(vector1, vector2):
	"""Return the sum of 3-dimension ``vector1`` and ``vector2``."""
	#TODO: convert it so it can handle vector of any dimension
	return (vector1[0] + vector2[0],
			vector1[1] + vector2[1],
			vector1[2] + vector2[2])


def sub3(vector1, vector2):
	"""Return the difference between 3-dimension ``vector1`` and ``vector2``."""
	#TODO: convert it so it can handle vector of any dimension
	return (vector1[0] - vector2[0],
			vector1[1] - vector2[1],
			vector1[2] - vector2[2])


def mult_by_scalar3(vector, scalar):
	"""Return 3-dimension ``vector`` multiplied by ``scalar``."""
	#TODO: convert it so it can handle vector of any dimension
	return (vector[0] * scalar, vector[1] * scalar, vector[2] * scalar)


def div_by_scalar3(vector, scalar):
	"""Return 3-dimension ``vector`` divided by ``scalar``."""
	#TODO: convert it so it can handle vector of any dimension
	return (vector[0] / scalar, vector[1] / scalar, vector[2] / scalar)


def dist3(vector1, vector2):
	"""Return the distance between point 3-dimension ``vector1`` and
	``vector2``.

	"""
	#TODO: convert it so it can handle vector of any dimension
	return length3(sub3(vector1, vector2))


def norm3(vector):
	"""Return the unit length vector parallel to 3-dimension ``vector``."""
	#l = length3(vector)
	#if l > 0.0:
	#	return (vector[0] / l, vector[1] / l, vector[2] / l)
	#else:
	#	return (0.0, 0.0, 0.0)
	return unitize(vector)


def unitize(vector_):
	"""Unitize a vector, i.e. return a unit-length vector parallel to
	``vector``.

	"""
	len_ = sqrt(sum(itertools.imap(operator.mul, vector_, vector_)))
	size_ = len(vector_)

	if len_ > 0.0:
		div_vector = (len_,) * size_  # (len_, len_, len_, ...)
		return tuple(itertools.imap(operator.div, vector_, div_vector))
	else:
		return (0.0, 0.0, 0.0)


def dot_product3(vector1, vector2):
	"""Return the dot product of 3-dimension ``vector1`` and ``vector2``."""
	return dot_product(vector1, vector2)


def dot_product(vec1, vec2):
	"""Efficient dot-product operation between two vectors of the same size.
	source: http://docs.python.org/library/itertools.html

	"""
	return sum(itertools.imap(operator.mul, vec1, vec2))


def cross_product(vector1, vector2):
	"""Return the cross product of 3-dimension ``vector1`` and ``vector2``."""
	return (vector1[1] * vector2[2] - vector1[2] * vector2[1],
		vector1[2] * vector2[0] - vector1[0] * vector2[2],
		vector1[0] * vector2[1] - vector1[1] * vector2[0])


def project3(vector, unit_vector):
	"""Return projection of 3-dimension ``vector`` onto unit 3-dimension
	``unit_vector``.

	"""
	#TODO: convert it so it can handle vector of any dimension
	return mult_by_scalar3(vector, dot_product3(norm3(vector), unit_vector))


def acos_dot3(vector1, vector2):
	"""Return the angle between unit 3-dimension ``vector1`` and ``vector2``."""
	x = dot_product3(vector1, vector2)
	if x < -1.0:
		return pi
	elif x > 1.0:
		return 0.0
	else:
		return acos(x)


def rotate3(rot, vector):
	"""Return the rotation of 3-dimension ``vector`` by 3x3 (row major) matrix
	``rot``.

	"""
	return (vector[0] * rot[0] + vector[1] * rot[1] +
			vector[2] * rot[2],
			vector[0] * rot[3] + vector[1] * rot[4] +
			vector[2] * rot[5],
			vector[0] * rot[6] + vector[1] * rot[7] +
			vector[2] * rot[8])


def transpose3(matrix):
	"""Return the inversion (transpose) of 3x3 rotation matrix ``matrix``."""
	#TODO: convert it so it can handle vector of any dimension
	return (matrix[0], matrix[3], matrix[6],
		matrix[1], matrix[4], matrix[7],
		matrix[2], matrix[5], matrix[8])


def z_axis(rot):
	"""Return the z-axis vector from 3x3 (row major) rotation matrix
	``rot``.

	"""
	#TODO: convert it so it can handle vector of any dimension, and any column
	return (rot[2], rot[5], rot[8])

#==============================================================================
# TESTS
#==============================================================================


def _test_angular_conversions(angle_):
	#x = 2.0/3*pi
	y = radians_to_degrees(angle_)
	z = degrees_to_radians(y)
	dif = angle_ - z

	print('radians: %f' % angle_)
	print('degrees: %f' % y)
	print('difference: %f' % dif)

if __name__ == '__main__':

	_test_angular_conversions(2.0 / 3 * pi)
	_test_angular_conversions(4.68 * pi)

	radians_ = (2.0 / 3 * pi, 2.0 * pi, 1.0 / 4 * pi)
	degrees_ = (120, 360, 45)
	print(vec3_radians_to_degrees(radians_))
	print(vec3_degrees_to_radians(degrees_))
	print(radians_)
