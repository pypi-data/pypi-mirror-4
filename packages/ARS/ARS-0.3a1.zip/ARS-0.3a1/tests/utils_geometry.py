
# TODO: create a test for calc_rotation_matrix

import numpy as np

import ars.utils.geometry as gemut
import ars.utils.mathematical as mut


def _test_Transform():

	pos = (10,20,30)
	rot = (0,0,1,1,0,0,0,1,0)
	t = gemut.Transform(pos, rot)

	print(pos)
	print(rot)
	print(t)
	print(t.get_long_tuple())

def _test_rot_matrix_to_hom_transform():

	rot1 = np.mat([[1,2,3],[4,5,6],[7,8,9]])
	rot2 = ((1,2,3),(4,5,6),(7,8,9))
	rot3 = (1,2,3,4,5,6,7,8,9)
	ht1 = gemut.rot_matrix_to_hom_transform(rot1)
	ht2 = gemut.rot_matrix_to_hom_transform(rot2)
	ht3 = gemut.rot_matrix_to_hom_transform(rot3)

	#print(rot1)
	#print(rot2)
	print(ht1)
	print(ht2)
	print(ht3)

def test_calc_inclination(axis, angle):
	#axis = mut.upAxis
	#angle = mut.pi/4
	rot_matrix = gemut.calc_rotation_matrix(axis, angle)
	pitch, roll = gemut.calc_inclination(rot_matrix)
	print('axis: %s, angle: %f' % (axis, angle))
	print('pitch: %f, roll: %f' % (pitch, roll))
	print('')

if __name__ == "__main__":

	_test_rot_matrix_to_hom_transform()

	_test_Transform()

	# rotation around axii perpendicular to the ground does not affect
	# the inclination
	test_calc_inclination(mut.upAxis, mut.pi/4)
	test_calc_inclination(mut.upAxis, 3*mut.pi/9)
	test_calc_inclination(mut.upAxis, -mut.pi/8)
	test_calc_inclination(mut.downAxis, mut.pi/4)
	test_calc_inclination(mut.downAxis, 3*mut.pi/9)
	test_calc_inclination(mut.downAxis, -mut.pi/8)

	test_calc_inclination(mut.rightAxis, mut.pi/6)
	test_calc_inclination(mut.rightAxis, 3*mut.pi/9)
	test_calc_inclination(mut.rightAxis, -mut.pi/8)
	test_calc_inclination(mut.leftAxis, mut.pi/8)
	test_calc_inclination(mut.bkwdAxis, mut.pi/8)

