#!/usr/bin/env python

# Created on 2012.01.30
#
# @author: german

"""
Runs a simulation of a vehicle with two powered wheels and one
free-rotating spherical wheel. It has a 2-link robotic arm attached,
with joints either friction-free or with friction proportional to
joint speed. The second joint has a PD controller.
"""

from VehicleWithArm import VehicleWithArm

def output_data(time, sp, cv, error, torque):

	print('time: %f, sp: %f, cv: %f, error: %f, torque: %f' %
		(time, sp, cv, error, torque))

class VehicleWithControlledArm(VehicleWithArm):

	WHEEL_R_PARAMS = ((0.4,0.3,(0,0,-0.5)),{'density':1}) # ((length, radius, center), density)
	WHEEL_L_PARAMS = ((0.4,0.3,(0,0,0.5)),{'density':1})

	SP_STEP = 0.1
	q2_SP = 0.0 # mut.pi/3 # set point
	R2_KP = 1.0 # controller proportional action
	R2_KD = 0.5 # controller derivative action

	def __init__(self, use_capsule_wheels=False, frictionless_arm=True):
		"""Constructor, calls the superclass constructor first"""
		VehicleWithArm.__init__(self, use_capsule_wheels, frictionless_arm)

		self.key_press_functions.add('d', self.increase_sp)
		self.key_press_functions.add('c', self.decrease_sp)

		self.sp = self.q2_SP
		self.previous_error = 0.0

	def on_pre_step(self):
		try:
			time = self.sim.sim_time
			time_step = self.sim.time_step
			cv = self.get_q2()

			mv = self.get_compensation(self.sp, cv, time_step)
			self.apply_torque_to_joints(0, mv) # torque1, torque2

			output_data(time, self.sp, cv, self.sp - cv, mv)

		except Exception as e:
			print('Exception when executing on_pre_step: %s' % str(e))

	def increase_sp(self):
		"""Increase angle set point"""
		self.sp += self.SP_STEP

	def decrease_sp(self):
		"""Decrease angle set point"""
		self.sp -= self.SP_STEP

	def get_q2(self):
		"""Get the current angle of the second rotary joint"""
		return self.sim.get_joint('r2').joint.angle

	def get_compensation(self, sp, q, time_step):
		"""Calculate the control torque with a PD controller"""
		error = (sp - q)
		error_p = (error - self.previous_error) / time_step
		torque = self.R2_KP * error + self.R2_KD * error_p
		self.previous_error = error
		return torque

if __name__ == '__main__':
	sim_program = VehicleWithControlledArm(False, False)
	sim_program.start()