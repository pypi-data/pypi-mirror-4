#!/usr/bin/env python

# Created on 2012.01.30
#
# @author: german

"""
Example #5. To achieve the same results reported in the paper,
the contact joint mu parameter (in ars.model.simulator.collision near_callback function)
must be set to 50, instead of the default 500 value.
"""
import os
import sys

# we need to add the parent directory to the Python path (PYTHONPATH)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from VehicleWithArm import VehicleWithArm

class Example5(VehicleWithArm):

	FPS = 50
	STEPS_PER_FRAME = 80
	CAMERA_POSITION = (15,10,15)
	PRINT_KEY_INFO = False

	WHEEL_TORQUE = 3

	WHEEL_R_PARAMS = ((0.4,0.3,(0,0,-0.5)),{'mass':1}) # ((length, radius, center), mass)
	WHEEL_L_PARAMS = ((0.4,0.3,(0,0,0.5)),{'mass':1})

	# joint 2 controller params
	SP_STEP = 0.1 # set point step
	q2_INITIAL_SP = 0.0 # initial set point
	R2_KP = 3.0 # controller proportional action
	R2_KD = 3.0 # controller derivative action

	def __init__(self, use_capsule_wheels=False, frictionless_arm=True):
		"""Constructor, calls the superclass constructor first"""
		VehicleWithArm.__init__(self, use_capsule_wheels, frictionless_arm)

		self.key_press_functions.add('d', self.increase_sp)
		self.key_press_functions.add('c', self.decrease_sp)

		self.sp = self.q2_INITIAL_SP
		self.previous_error = 0.0
		self.torque_w1 = 0.0
		self.torque_w2 = 0.0

	def on_pre_step(self):
		try:
			time = self.sim.sim_time
			time_step = self.sim.time_step
			pos = self.sim.get_object(self.chassis).get_position()
			q1 = self.sim.get_joint('r1').joint.angle
			q2 = self.sim.get_joint('r2').joint.angle

			mv = self.get_compensation(self.sp, q2, time_step)
			self.apply_torque_to_joints(0, mv) # torque1, torque2

			print('%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e' %
				(time,pos[0],pos[2],q1,q2,self.sp,mv,self.torque_w1,self.torque_w2))

			self.torque_w1 = 0.0
			self.torque_w2 = 0.0

		except Exception as e:
			print('Exception when executing on_pre_step: %s' % str(e))

	def apply_torque_to_wheels(self, torque1, torque2):
		VehicleWithArm.apply_torque_to_wheels(self, torque1, torque2)
		self.torque_w1 = torque1
		self.torque_w2 = torque2

	def increase_sp(self):
		"""Increase angle set point"""
		self.sp += self.SP_STEP

	def decrease_sp(self):
		"""Decrease angle set point"""
		self.sp -= self.SP_STEP

	def get_compensation(self, sp, q, time_step):
		"""Calculate the control torque with a PD controller"""
		error = (sp - q)
		error_p = (error - self.previous_error) / time_step
		torque = self.R2_KP * error + self.R2_KD * error_p
		self.previous_error = error
		return torque

if __name__ == '__main__':
	sim_program = Example5(False, False)
	sim_program.start()