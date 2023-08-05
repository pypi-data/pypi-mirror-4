#!/usr/bin/env python

# Created on 2012.01.03
#
# @author: german

"""
Runs a simulation of a vehicle with two powered wheels and one
free-rotating spherical wheel. It has a 2-link robotic arm attached,
with joints either friction-free or with friction proportional to
joint speed.
"""

from ars.app import Program
import ars.utils.mathematical as mut
import ars.constants as cts
from ars.lib.pydispatch import dispatcher
from ars.model.simulator import SIM_PRE_STEP_SIGNAL

class VehicleWithArm(Program):

	STEPS_PER_FRAME = 200
	BACKGROUND_COLOR = (0.8,0.8,0.8)
	FLOOR_BOX_SIZE = (20,0.01,20)

	WHEEL_TORQUE = 3
	VEHICLE_OFFSET = (2,0.35,4)

	BALL_PARAMS = ((0.3,(1,0,0)),{'density':1}) # ((radius, center), density)
	CHASSIS_PARAMS = (((2,0.2,1.5),(0.5,0.45,0)),{'mass':6}) # ((size, center), mass)

	WHEEL_R_PARAMS = ((0.4,0.3,(0,0,-0.5)),{'density':1}) # ((length, radius, center), density)
	WHEEL_L_PARAMS = ((0.4,0.3,(0,0,0.5)),{'density':1})

	LINK1_PARAMS = ((0.8, 0.1,(0,0,0)),{'density':1}) # ((length, radius, center), density)
	LINK2_PARAMS = ((0.6,0.1,(0,0.7,0.2)),{'density':1})

	R1_TORQUE = 3

	Q1_FRICTION_COEFF = 0.01
	Q2_FRICTION_COEFF = 0.01

	def __init__(self, use_capsule_wheels=False, frictionless_arm=True):
		"""Constructor, calls the superclass constructor first"""
		self._use_capsule_wheels = use_capsule_wheels
		self._frictionless_arm = frictionless_arm

		Program.__init__(self)
		self.key_press_functions.add('up', self.go_forwards, repeat=True)
		self.key_press_functions.add('down', self.go_backwards, repeat=True)
		self.key_press_functions.add('left', self.turn_left, repeat=True)
		self.key_press_functions.add('right', self.turn_right, repeat=True)

		self.key_press_functions.add('a', self.rotate_clockwise)
		self.key_press_functions.add('z', self.rotate_counterlockwise)

		dispatcher.connect(self.on_pre_step, SIM_PRE_STEP_SIGNAL)

	def create_sim_objects(self):
		"""Implementation of the required method. Creates and sets up all the
		objects of the simulation."""

		arm_offset = (0,0.5,0)

		#=======================================================================
		# VEHICLE
		#=======================================================================

		if self._use_capsule_wheels:
			wheelR = self.sim.add_capsule(*self.WHEEL_R_PARAMS[0], **self.WHEEL_R_PARAMS[1])
			wheelL = self.sim.add_capsule(*self.WHEEL_L_PARAMS[0], **self.WHEEL_L_PARAMS[1])
		else:
			wheelR = self.sim.add_cylinder(*self.WHEEL_R_PARAMS[0], **self.WHEEL_R_PARAMS[1])
			wheelL = self.sim.add_cylinder(*self.WHEEL_L_PARAMS[0], **self.WHEEL_L_PARAMS[1])

		ball = self.sim.add_sphere(*self.BALL_PARAMS[0], **self.BALL_PARAMS[1])
		chassis = self.sim.add_box(*self.CHASSIS_PARAMS[0], **self.CHASSIS_PARAMS[1])

		self.sim.add_rotary_joint('w1',                   # name, obj1, obj2, anchor, axis
							self.sim.get_object(chassis),
							self.sim.get_object(wheelR),
							None, cts.Z_AXIS)
		self.sim.add_rotary_joint('w2',
							self.sim.get_object(chassis),
							self.sim.get_object(wheelL),
							None, cts.Z_AXIS)
		self.sim.add_ball_socket_joint('bs',              # name, obj1, obj2, anchor
								self.sim.get_object(chassis),
								self.sim.get_object(ball),
								None)

		self.sim.get_object(wheelR).offset_by_position(self.VEHICLE_OFFSET)
		self.sim.get_object(wheelL).offset_by_position(self.VEHICLE_OFFSET)
		self.sim.get_object(ball).offset_by_position(self.VEHICLE_OFFSET)
		self.sim.get_object(chassis).offset_by_position(self.VEHICLE_OFFSET)

		#=======================================================================
		# ROBOTIC ARM
		#=======================================================================
		link1 = self.sim.add_capsule(*self.LINK1_PARAMS[0], **self.LINK1_PARAMS[1])
		link2 = self.sim.add_capsule(*self.LINK2_PARAMS[0], **self.LINK2_PARAMS[1])

		# bodies are rotated before attaching themselves through joints
		self.sim.get_object(link1).rotate(cts.X_AXIS, mut.pi/2)
		self.sim.get_object(link2).rotate(cts.X_AXIS, mut.pi/2)

		self.sim.get_object(link1).offset_by_object(self.sim.get_object(chassis))
		self.sim.get_object(link1).offset_by_position(arm_offset)
		self.sim.get_object(link2).offset_by_object(self.sim.get_object(link1))

		self.sim.add_rotary_joint('r1',				   # name, obj1, obj2, anchor, axis
							self.sim.get_object(chassis),
							self.sim.get_object(link1),
							None, cts.Y_AXIS)
		r2_anchor = mut.sub3(self.sim.get_object(link2).get_position(),
							(0,self.LINK2_PARAMS[0][0]/2,0)) # (0,length/2,0)
		self.sim.add_rotary_joint('r2',
							self.sim.get_object(link1),
							self.sim.get_object(link2),
							r2_anchor, cts.Z_AXIS)

		self.sim.get_object(chassis).actor.set_color(cts.COLOR_RED)
		self.sim.get_object(link1).actor.set_color(cts.COLOR_YELLOW)
		self.sim.get_object(link2).actor.set_color(cts.COLOR_NAVY)

		self.chassis = chassis
		self.wheelR = wheelR
		self.wheelL = wheelL
		self.ball = ball

		self.link1 = link1
		self.link2 = link2

	def go_forwards(self):
		"""Rotate both powered wheels in the same direction, forwards"""
		self.apply_torque_to_wheels(self.WHEEL_TORQUE, self.WHEEL_TORQUE)

	def go_backwards(self):
		"""Rotate both powered wheels in the same direction, backwards"""
		self.apply_torque_to_wheels(-self.WHEEL_TORQUE, -self.WHEEL_TORQUE)

	def turn_left(self):
		"""Rotate both powered wheels in different directions, with a global
		counter-clockwise rotation (from above)"""
		self.apply_torque_to_wheels(-self.WHEEL_TORQUE, self.WHEEL_TORQUE)

	def turn_right(self):
		"""Rotate both powered wheels in different directions, with a global
		clockwise rotation (from above)"""
		self.apply_torque_to_wheels(self.WHEEL_TORQUE, -self.WHEEL_TORQUE)

	def on_pre_step(self):
		#print(self.sim.get_object(self.chassis).get_position())
		try:
			#time = self.sim.sim_time
			q1p = self.get_q1p()
			q2p = self.get_q2p()

			if not self._frictionless_arm:
				self.apply_friction(q1p, q2p)

			print('q1p: %f, q2p: %f' % (q1p, q2p))

		except Exception as e:
			print('Exception when executing on_pre_step: %s' % str(e))

	def apply_torque_to_wheels(self, torque1, torque2):
		if torque1 is not None:
			self.sim.get_joint('w1').add_torque(torque1)
		if torque2 is not None:
			self.sim.get_joint('w2').add_torque(torque2)

	def rotate_clockwise(self):
		self.apply_torque_to_joints(self.R1_TORQUE, 0)

	def rotate_counterlockwise(self):
		self.apply_torque_to_joints(-self.R1_TORQUE, 0)

	def apply_torque_to_joints(self, torque1, torque2):
		if torque1 is not None:
			self.sim.get_joint('r1').add_torque(torque1)
		if torque2 is not None:
			self.sim.get_joint('r2').add_torque(torque2)

	def get_q1p(self):
		return self.sim.get_joint('r1').joint.angle_rate

	def get_q2p(self):
		return self.sim.get_joint('r2').joint.angle_rate

	def apply_friction(self, q1p, q2p):
		self.apply_torque_to_joints(-q1p * self.Q1_FRICTION_COEFF, -q2p * self.Q2_FRICTION_COEFF)

if __name__ == '__main__':
	sim_program = VehicleWithArm()
	sim_program.start()