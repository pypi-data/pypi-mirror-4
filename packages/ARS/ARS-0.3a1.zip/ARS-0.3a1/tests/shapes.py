

# Created on 2012.01.30
#
# @author: german
#

import ars.model.geometry.base as sh

def test_get_heightfield_faces():
	print(sh.Trimesh.get_heightfield_faces(5, 5))

if __name__ == '__main__':
	test_get_heightfield_faces()