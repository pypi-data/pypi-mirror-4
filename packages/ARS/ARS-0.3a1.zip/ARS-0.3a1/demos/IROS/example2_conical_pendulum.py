#!/usr/bin/env python

# Created on 2012.03.09
#
# @author: german

"""
Example #2
"""

from ars.app import Program, Simulation
from ars.lib.pydispatch import dispatcher
import ars.model.simulator
import ars.utils.mathematical as mut
import ars.constants as cts

SIM_PRE_STEP_SIGNAL = ars.model.simulator.SIM_PRE_STEP_SIGNAL

class Example2(Program):
	
	# simulation & window parameters
	CAMERA_POSITION = (6,3,6)
	FPS = 50
	STEPS_PER_FRAME = 80
	
	# bodies' parameters
	DELTA = 0.01 # to prevent the collision of the 2nd link with the floor
	OFFSET = (1,0,2)
	BOX_PARAMS = (((10,0.5,10),(0,-0.25,0)),{'density':100}) # ((size, center), density)
	
	POLE_RADIUS = 0.141421 # 1/(5*sqrt(2))
	POLE_HEIGHT = 1
	POLE_INITIAL_POS = (0.0,0.5 + DELTA,0.0)
	POLE_MASS = 10.0
	
	ARM_RADIUS = 0.141421
	ARM_LENGTH = 1.0
	ARM_INITIAL_POS = (0.0,0.5 + DELTA,0.1)
	ARM_MASS = 10.0
	
	JOINT1_ANCHOR = (0.0,0.0,0.0)
	JOINT1_AXIS = cts.Y_AXIS
	JOINT2_ANCHOR = (0.0,1.0 + DELTA,0.1)
	JOINT2_AXIS = cts.X_AXIS
	
	Q1_FRICTION_COEFF = 50e-3 * 100
	Q2_FRICTION_COEFF = 50e-3 * 100

	# control
	MAX_TORQUE = 20
	SATURATION_TIME = 1

	def __init__(self):
		Program.__init__(self)
		dispatcher.connect(self.on_pre_step, SIM_PRE_STEP_SIGNAL)
		
		self.q1p_prev = 0.0
		self.q2p_prev = 0.0
		
	def create_simulation(self):
		# we didn't need to code this method
		# but if we want to modify the floor, we have to
		
		# set up the simulation parameters
		self.sim = Simulation(self.FPS, self.STEPS_PER_FRAME)
		self.sim.add_basic_simulation_objects()
		self.sim.add_axes()
		self.sim.add_floor(normal=(0,1,0), box_size=self.FLOOR_BOX_SIZE, 
						color=(0.7,0.7,0.7), dist=-0.5, box_center=(0,-0.5,0))
		
		self.create_sim_objects()
		
		# add the graphic objects
		self.gAdapter.add_objects_list(self.sim.actors.values())
		self.sim.update_actors()
	
	def create_sim_objects(self):
		box = self.sim.add_box(*self.BOX_PARAMS[0], **self.BOX_PARAMS[1])
		
		pole = self.sim.add_cylinder(self.POLE_HEIGHT, self.POLE_RADIUS, 
									self.POLE_INITIAL_POS, mass=self.POLE_MASS)
		arm = self.sim.add_cylinder(self.ARM_LENGTH, self.ARM_RADIUS, 
									self.ARM_INITIAL_POS, mass=self.ARM_MASS)
		
		# bodies are rotated before attaching themselves through joints
		self.sim.get_object(pole).rotate(cts.X_AXIS, mut.pi/2)
		self.sim.get_object(arm).rotate(cts.X_AXIS, mut.pi/2)
		
		self.sim.get_object(box).offset_by_position(self.OFFSET)
		self.sim.get_object(pole).offset_by_position(self.OFFSET)
		self.sim.get_object(arm).offset_by_position(self.OFFSET)
		
		self.sim.add_rotary_joint('r1',         # name, obj1, obj2, anchor, axis
							self.sim.get_object(box), 
							self.sim.get_object(pole),
							None,
							self.JOINT1_AXIS)
		
		self.sim.add_rotary_joint('r2', 
							self.sim.get_object(pole), 
							self.sim.get_object(arm), 
							mut.add3(self.OFFSET, self.JOINT2_ANCHOR),
							self.JOINT2_AXIS)
		
		#self.sim.get_object(box).actor.set_color(cts.COLOR_RED)
		self.sim.get_object(pole).actor.set_color(cts.COLOR_YELLOW)
		self.sim.get_object(arm).actor.set_color(cts.COLOR_NAVY)
		
		self.box = box
		self.pole = pole
		self.arm = arm

	def on_pre_step(self):
		try:
			time = self.sim.sim_time
			torque1 = self.get_torque_to_apply(time)
			
			self.apply_torque_to_joints(torque1, None)
			self.apply_friction(self.q1p_prev, self.q2p_prev)
			
			q1 = self.get_q1()
			q2 = self.get_q2()
			q1p = self.get_q1p()
			q2p = self.get_q2p()
		
			self.q1p_prev = q1p
			self.q2p_prev = q2p
		
			print('%.7e\t%.7e\t%.7e\t%.7e\t%.7e' % (time,q1,q1p,q2,q2p))
			
		except Exception as e:
			print('Exception when executing on_pre_step: %s' % str(e))
	
	def get_torque_to_apply(self, time):
		if time < self.SATURATION_TIME:
			torque = time * self.MAX_TORQUE
		else:
			torque = self.MAX_TORQUE
		return torque
	
	def get_q1(self):
		return self.sim.get_joint('r1').joint.angle
	
	def get_q2(self):
		return self.sim.get_joint('r2').joint.angle
	
	def get_q1p(self):
		return self.sim.get_joint('r1').joint.angle_rate
	
	def get_q2p(self):
		return self.sim.get_joint('r2').joint.angle_rate
	
	def apply_torque_to_joints(self, torque1, torque2):
		if torque1 is not None:
			self.sim.get_joint('r1').add_torque(torque1)
		if torque2 is not None:
			self.sim.get_joint('r2').add_torque(torque2)
	
	def apply_friction(self, q1p, q2p):
		self.apply_torque_to_joints(-q1p * self.Q1_FRICTION_COEFF,
								-q2p * self.Q2_FRICTION_COEFF)

if __name__ == '__main__':
	sim_program = Example2()
	sim_program.start()
	
	# print arm links' inertia matrices
	pole_body = sim_program.sim.get_object(sim_program.pole).body
	arm_body = sim_program.sim.get_object(sim_program.arm).body
	print(pole_body.get_inertia_tensor())
	print(arm_body.get_inertia_tensor())