#!/usr/bin/env python

# Created on 2011.11.16
#
# @author: german

from ars.app import Program

class Vehicle1(Program):
	
	TORQUE = 500
	
	def __init__(self):
		Program.__init__(self)
		self.key_press_functions.add('up', self.go_forwards)
		self.key_press_functions.add('down', self.go_backwards)
		self.key_press_functions.add('left', self.turn_left)
		self.key_press_functions.add('right', self.turn_right)
	
	def create_sim_objects(self):
		# POR: point of reference
		wheel1 = self.sim.add_cylinder(0.1, 0.2, (1,1,1), density=1) # length, radius, center, density
		
		wheel2 = self.sim.add_cylinder(0.1, 0.2, (0,0,1), density=1)
		wheel3 = self.sim.add_cylinder(0.1, 0.2, (1,0,0), density=1)
		wheel4 = self.sim.add_cylinder(0.1, 0.2, (1,0,1), density=1)
		
		chassis = self.sim.add_box((1.3,0.2,0.6), (0.5,0,0.5), density=10) # size, center, density
		
		self.sim.get_object(wheel2).offset_by_object(self.sim.get_object(wheel1))
		self.sim.get_object(wheel3).offset_by_object(self.sim.get_object(wheel1))
		self.sim.get_object(wheel4).offset_by_object(self.sim.get_object(wheel1))
		self.sim.get_object(chassis).offset_by_object(self.sim.get_object(wheel1))
		
		self.sim.add_rotary_joint('r1', self.sim.get_object(chassis), 
								self.sim.get_object(wheel1), (1,1,1), (0,0,1)) # name, obj1, obj2, anchor, axis
		self.sim.add_rotary_joint('r2', self.sim.get_object(chassis), 
								self.sim.get_object(wheel2), (1,1,2), (0,0,1))
		self.sim.add_rotary_joint('r3', self.sim.get_object(chassis), 
								self.sim.get_object(wheel3), (2,1,1), (0,0,1))
		self.sim.add_rotary_joint('r4', self.sim.get_object(chassis), 
								self.sim.get_object(wheel4), (2,1,2), (0,0,1))
	
	def go_forwards(self):
		self.sim.get_joint('r1').add_torque(self.TORQUE)
		self.sim.get_joint('r2').add_torque(self.TORQUE)
	
	def go_backwards(self):
		self.sim.get_joint('r1').add_torque(-self.TORQUE)
		self.sim.get_joint('r2').add_torque(-self.TORQUE)
		
	def turn_left(self):
		self.sim.get_joint('r1').add_torque(-self.TORQUE/2)
		self.sim.get_joint('r3').add_torque(-self.TORQUE/2)
		self.sim.get_joint('r2').add_torque(self.TORQUE/2)
		self.sim.get_joint('r4').add_torque(self.TORQUE/2)
		
	def turn_right(self):
		self.sim.get_joint('r1').add_torque(self.TORQUE/2)
		self.sim.get_joint('r3').add_torque(self.TORQUE/2)
		self.sim.get_joint('r2').add_torque(-self.TORQUE/2)
		self.sim.get_joint('r4').add_torque(-self.TORQUE/2)

if __name__ == '__main__':
	sim_program = Vehicle1()
	sim_program.start()