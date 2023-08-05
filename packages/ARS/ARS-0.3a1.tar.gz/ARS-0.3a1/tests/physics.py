
# Created on 2012.03.09
#
# @author: german
import math

from ars.app import Program


def sphere_volume(radius):
	return 4.0/3.0 * math.pi * (radius ** 3)


class BodyTest1(Program):
	def create_sim_objects(self):
		self.sim.add_sphere(0.5, (1,10,1), density=1) # radius, center, density

class BodyTest2(Program):
	def create_sim_objects(self):
		self.sim.add_cylinder(length=1.0, radius=1.0, center=(10,10,25), mass=4.67)

class BodyTest3(Program):
	def create_sim_objects(self):
		self.sim.add_sphere(0.5, (1,10,1), mass=1) # radius, center, mass

def run_body_test():

	# body.get_center_of_gravity() is always (0,0,0) unless changed explicitly

	sim_program = BodyTest1()
	sim_program.start()
	body = sim_program.sim.get_object("sphere").body
	print(body.get_position())
	print('%s / %s' % (1.0 * sphere_volume(0.5), body.get_mass()))
	print(body.get_inertia_tensor())
	
	sim_program = BodyTest2()
	sim_program.start()
	body = sim_program.sim.get_object("cylinder").body
	print(body.get_position())
	print('%s / %s' % (4.67, body.get_mass()))
	print(body.get_inertia_tensor())
	
	sim_program = BodyTest3()
	sim_program.start()
	body = sim_program.sim.get_object("sphere").body
	print(body.get_position())
	print('%s / %s' % (1.0, body.get_mass()))
	print(body.get_inertia_tensor())

if __name__ == '__main__':
	run_body_test()