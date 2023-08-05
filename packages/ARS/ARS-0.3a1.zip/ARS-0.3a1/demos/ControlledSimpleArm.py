#!/usr/bin/env python

# Created on 2011.12.01
#
# @author: german

"""
Runs a simulation of a controlled (PD) simple arm, with 2 links and 2 rotary joints.
There's friction proportional to angle speed, for both joints.
"""

from ars.app import Program
import ars.utils.mathematical as mut
import ars.constants as cts
from ars.lib.pydispatch import dispatcher
from ars.model.simulator import SIM_PRE_STEP_SIGNAL

def output_data(time, sp, cv, error, torque):

	print('time: %f, sp: %f, cv: %f, error: %f, torque: %f' %
		(time, sp, cv, error, torque))

class ControlledSimpleArm(Program):

	R1_TORQUE = 3

	OFFSET = (2.5,1,2.5)

	BOX_PARAMS = (((3,0.5,3),(0,-0.75,0)),{'density':1}) # ((size, center), density)
	LINK1_PARAMS = ((0.8, 0.1,(0,0,0)),{'density':1}) # ((length, radius, center), density)
	LINK2_PARAMS = ((0.6,0.1,(0,0.7,0.2)),{'density':1})

	SP_STEP = 0.1
	q2_INITIAL_SP = 0.0 # mut.pi/3 # set point
	R2_KP = 1.0 # controller proportional action
	R2_KD = 0.5 # controller derivative action

	Q1_FRICTION_COEFF = 0.01
	Q2_FRICTION_COEFF = 0.01

	def __init__(self):
		Program.__init__(self)
		self.key_press_functions.add('a', self.rotate_clockwise)
		self.key_press_functions.add('z', self.rotate_counterlockwise)
		self.key_press_functions.add('d', self.increase_sp)
		self.key_press_functions.add('c', self.decrease_sp)

		dispatcher.connect(self.on_pre_step, SIM_PRE_STEP_SIGNAL)

		self.sp = self.q2_INITIAL_SP
		self.previous_error = 0.0

	def create_sim_objects(self):

		box = self.sim.add_box(*self.BOX_PARAMS[0], **self.BOX_PARAMS[1])
		link1 = self.sim.add_capsule(*self.LINK1_PARAMS[0], **self.LINK1_PARAMS[1])
		link2 = self.sim.add_capsule(*self.LINK2_PARAMS[0], **self.LINK2_PARAMS[1])

		# bodies are rotated before attaching themselves through joints
		self.sim.get_object(link1).rotate(cts.X_AXIS, mut.pi/2)
		self.sim.get_object(link2).rotate(cts.X_AXIS, mut.pi/2)

		self.sim.get_object(box).offset_by_position(self.OFFSET)
		self.sim.get_object(link1).offset_by_position(self.OFFSET)
		self.sim.get_object(link2).offset_by_position(self.OFFSET)

		self.sim.add_rotary_joint('r1',					# name, obj1, obj2, anchor, axis
							self.sim.get_object(box),
							self.sim.get_object(link1),
							None, cts.Y_AXIS)
		r2_anchor = mut.sub3(self.sim.get_object(link2).get_position(),
							(0,self.LINK2_PARAMS[0][0]/2,0)) # (0, length/2, 0)
		self.sim.add_rotary_joint('r2',
							self.sim.get_object(link1),
							self.sim.get_object(link2),
							r2_anchor, cts.Z_AXIS)

	def on_pre_step(self):
		try:
			time = self.sim.sim_time
			time_step = self.sim.time_step
			cv = self.get_q2()
			q1p = self.get_q1p()
			q2p = self.get_q2p()

			mv = self.get_compensation(self.sp, cv, time_step)
			self.apply_torque_to_joints(0, mv)
			self.apply_friction(q1p, q2p)

			output_data(time, self.sp, cv, self.sp - cv, mv)
			#print('q1p: %f, q2p: %f' % (q1p, q2p))

		except Exception as e:
			print('Exception when executing on_pre_step: %s' % str(e))

	def rotate_clockwise(self):
		self.apply_torque_to_joints(self.R1_TORQUE, 0)

	def rotate_counterlockwise(self):
		self.apply_torque_to_joints(-self.R1_TORQUE, 0)

	def apply_torque_to_joints(self, torque1, torque2):
		if torque1 is not None:
			self.sim.get_joint('r1').add_torque(torque1)
		if torque2 is not None:
			self.sim.get_joint('r2').add_torque(torque2)

	def increase_sp(self):
		self.sp += self.SP_STEP

	def decrease_sp(self):
		self.sp -= self.SP_STEP

	def get_q2(self):
		return self.sim.get_joint('r2').joint.angle

	def get_q1p(self):
		return self.sim.get_joint('r1').joint.angle_rate

	def get_q2p(self):
		return self.sim.get_joint('r2').joint.angle_rate

	def get_compensation(self, sp, q, time_step):
		"""PD controller"""
		error = (sp - q)
		error_p = (error - self.previous_error) / time_step
		torque = self.R2_KP * error + self.R2_KD * error_p
		self.previous_error = error
		return torque

	def apply_friction(self, q1p, q2p):
		self.apply_torque_to_joints(-q1p * self.Q1_FRICTION_COEFF, -q2p * self.Q2_FRICTION_COEFF)

if __name__ == '__main__':
	print('Python file being executed: %s' % __file__)
	sim_program = ControlledSimpleArm()
	sim_program.start()