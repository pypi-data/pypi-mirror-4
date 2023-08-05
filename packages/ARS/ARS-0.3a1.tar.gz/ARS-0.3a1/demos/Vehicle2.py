#!/usr/bin/env python

# Created on 2011.11.16
#
# @author: german

"""
Runs a simulation of a vehicle with two powered wheels and one
free-rotating spherical wheel.
"""

from ars.app import Program
import ars.constants as cts

class Vehicle2(Program):

	TORQUE = 30

	OFFSET = (3,1,3)

	FLOOR_BOX_SIZE = (20,0.01,20)

	def __init__(self):
		"""Constructor, calls the superclass constructor first"""
		Program.__init__(self)
		self.key_press_functions.add('up', self.go_forwards, True)
		self.key_press_functions.add('down', self.go_backwards, True)
		self.key_press_functions.add('left', self.turn_left, True)
		self.key_press_functions.add('right', self.turn_right, True)

	def create_sim_objects(self):
		"""Implementation of the required method. Creates and sets up all the
		objects of the simulation."""

		offset = self.OFFSET

		wheelR = self.sim.add_cylinder(0.4, 0.3, (0,0,-0.5), density=1) # length, radius, center, density
		wheelL = self.sim.add_cylinder(0.4, 0.3, (0,0,0.5), density=1)
		ball = self.sim.add_sphere(0.3, (1,0,0), density=1) # radius, center, density
		chassis = self.sim.add_box((2,0.2,1.5), (0.5,0.45,0), density=10) # size, center, density

		self.sim.add_rotary_joint('r1',				   # name, obj1, obj2, anchor, axis
							self.sim.get_object(chassis),
							self.sim.get_object(wheelR),
							None, cts.Z_AXIS)
		self.sim.add_rotary_joint('r2',
							self.sim.get_object(chassis),
							self.sim.get_object(wheelL),
							None, cts.Z_AXIS)
		self.sim.add_ball_socket_joint('bs',			  # name, obj1, obj2, anchor
								self.sim.get_object(chassis),
								self.sim.get_object(ball),
								None)

		self.sim.get_object(wheelR).offset_by_position(offset)
		self.sim.get_object(wheelL).offset_by_position(offset)
		self.sim.get_object(ball).offset_by_position(offset)
		self.sim.get_object(chassis).offset_by_position(offset)

		# test
		#print(self.sim.get_object(wheelR).actor.set_color((0.8,0,0)))


	def go_forwards(self):
		"""Rotate both powered wheels in the same direction, forwards"""
		self.sim.get_joint('r1').add_torque(self.TORQUE)
		self.sim.get_joint('r2').add_torque(self.TORQUE)

	def go_backwards(self):
		"""Rotate both powered wheels in the same direction, backwards"""
		self.sim.get_joint('r1').add_torque(-self.TORQUE)
		self.sim.get_joint('r2').add_torque(-self.TORQUE)

	def turn_left(self):
		"""Rotate both powered wheels in different directions, with a global
		counter-clockwise rotation (from above)"""
		self.sim.get_joint('r1').add_torque(-self.TORQUE)
		self.sim.get_joint('r2').add_torque(self.TORQUE)

	def turn_right(self):
		"""Rotate both powered wheels in different directions, with a global
		clockwise rotation (from above)"""
		self.sim.get_joint('r1').add_torque(self.TORQUE)
		self.sim.get_joint('r2').add_torque(-self.TORQUE)

if __name__ == '__main__':
	sim_program = Vehicle2()
	sim_program.start()