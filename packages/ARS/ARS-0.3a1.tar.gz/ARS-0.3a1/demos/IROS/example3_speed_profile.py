#!/usr/bin/env python

# Created on 2012.01.11
#
# @author: german

"""
Example #3
"""

import os
import sys

import ars.exceptions as exc

# we need to add the parent directory to the Python path (PYTHONPATH)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from VehicleWithArm import VehicleWithArm, mut

class Example3(VehicleWithArm):

	#WINDOW_SIZE = (1024,630)
	CAMERA_POSITION = (0,8,25) # (0,8,15)

	FPS = 50
	STEPS_PER_FRAME = 80

	VEHICLE_OFFSET = (-4,0.5,4)

	LINK1_PARAMS = ((0.8, 0.1,(0,0,0)),{'mass':1}) # ((length, radius, center), mass)
	LINK2_PARAMS = ((0.6,0.1,(0,0.7,0.2)),{'mass':1})

	Q1_FRICTION_COEFF = 0.02
	Q2_FRICTION_COEFF = 0.02

	KP = 10 # controller proportional action

	# speed profile setup
	speeds = ((0,0), (1,0), (5,1), (9,1), (13,0), (14,0)) # (time,speed)
	speed_i = 0

	def __init__(self):
		"""Constructor, calls the superclass constructor first"""
		VehicleWithArm.__init__(self)
		self.sim.get_object(self.chassis).actor.set_color((0.8,0,0))

		self.r1_angle_rate_prev = 0.0
		self.r2_angle_rate_prev = 0.0

	def on_pre_step(self):
		try:
			time = self.sim.sim_time

			if self.speed_i < len(self.speeds) - 1:
				if time > self.speeds[self.speed_i + 1][0]:
					self.speed_i += 1
			elif self.speed_i == len(self.speeds) - 1:
				pass

			pos = self.sim.get_object(self.chassis).get_position()
			q1 = self.sim.get_joint('r1').joint.angle
			q1p = self.sim.get_joint('r1').joint.angle_rate
			q2 = self.sim.get_joint('r2').joint.angle
			q2p = self.sim.get_joint('r2').joint.angle_rate

			linear_vel = self.sim.get_object(self.chassis).get_linear_velocity()
			linear_vel_XZ = (linear_vel[0], linear_vel[2])
			cv = mut.length2(linear_vel_XZ) * mut.sign(linear_vel[0])

			sp = self.calc_desired_speed(time)
			torque = self.compensate(sp, cv)
			self.apply_torque_to_wheels(torque, torque)
			self.apply_friction(q1p, q2p)

			print('%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e' %
				(time,pos[0],cv,sp,q1,q1p,q2,q2p,torque))

		except Exception as e:
			print('Exception when executing on_pre_step: %s' % str(e))

	def calc_desired_speed(self, time):

		if self.speed_i == len(self.speeds) - 1:
			return float(self.speeds[self.speed_i][1])

		elif 0 <= self.speed_i < len(self.speeds) - 1:
			time_diff = time - self.speeds[self.speed_i][0]
			time_period = self.speeds[self.speed_i + 1][0] - self.speeds[self.speed_i][0]
			prev_speed = float(self.speeds[self.speed_i][1])
			next_speed = float(self.speeds[self.speed_i + 1][1] )
			return (next_speed - prev_speed) * (time_diff / time_period) + prev_speed
		else:
			raise exc.ArsError('invalid speed_i value: %d' % self.speed_i)

	def compensate(self, sp, cv):
		return (sp - cv) * self.KP

if __name__ == '__main__':
	sim_program = Example3()
	sim_program.start()

	# print mass of bodies defined with a density value
	ball_body = sim_program.sim.get_object(sim_program.ball).body
	chassis_body = sim_program.sim.get_object(sim_program.chassis).body
	wheelR_body = sim_program.sim.get_object(sim_program.wheelR).body
	wheelL_body = sim_program.sim.get_object(sim_program.wheelL).body
	print(ball_body.get_mass())
	print(chassis_body.get_mass())
	print(wheelR_body.get_mass())
	print(wheelL_body.get_mass())