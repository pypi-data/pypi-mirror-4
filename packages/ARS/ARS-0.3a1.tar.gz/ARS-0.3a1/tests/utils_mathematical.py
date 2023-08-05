
# Created on 2011.12.01
#
# @author: german

import ars.utils.mathematical as mut


def _vector_diff_length(v1, v2):
	return mut.length3(mut.sub3(v1, v2))


def test_matrix_multiply():
	print (mut.matrix3_multiply(((2,0,0),(0,1,0),(0,0,1)),
		((1,0,0),(0,2,0),(0,0,1))))


def test_XYZ_axes_for_orthogonality():
	X = mut.X_AXIS
	Y = mut.Y_AXIS
	Z = mut.Z_AXIS
	print(_vector_diff_length(mut.cross_product(X, Y), Z))
	print(_vector_diff_length(mut.cross_product(Z, X), Y))
	print(_vector_diff_length(mut.cross_product(Y, Z), X))


if __name__ == "__main__":

	test_matrix_multiply()
	test_XYZ_axes_for_orthogonality()