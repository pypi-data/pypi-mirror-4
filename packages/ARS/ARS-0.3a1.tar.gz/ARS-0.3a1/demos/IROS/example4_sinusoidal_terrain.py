#!/usr/bin/env python

# Created on 2012.01.16
#
# @author: german

"""
Example #4
"""
import os
import sys
from random import random

from ars.lib.pydispatch import dispatcher
from ars.model.collision.base import Trimesh
from ars.model.simulator import Simulation, SIM_PRE_STEP_SIGNAL
import ars.utils.mathematical as mut

# we need to add the parent directory to the Python path (PYTHONPATH)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from VehicleWithArm import VehicleWithArm

def random_heightfield(num_x, num_z, scale=1.0):
	"""A height field where values are completely random"""
	# that x and z are integers, not floats, does not matter
	verts=[]
	for x in range(num_x):
		for z in range(num_z):
			verts.append( (x,random()*scale,z) )
	return verts

def sinusoidal_heightfield(num_x, num_z, height_scale=1.0, frequency_x=1.0):
	"""Creates the vertices corresponding to a sinusoidal heightfield along the
	X axis. The height_scale controls the amplitude of the wave, and
	frequency_x its frequency"""
	# TODO: fix the frequency units
	verts=[]
	for x in range(num_x):
		for z in range(num_z):
			verts.append( (x, mut.sin(x * frequency_x)*height_scale, z) )
	return verts

def constant_heightfield(num_x, num_z, height=0.0):
	"""A height field where all the values are the same"""
	# that x and z are integers, not floats, does not matter
	verts=[]
	for x in range(num_x):
		for z in range(num_z):
			verts.append((x, height, z))
	return verts

class Example4(VehicleWithArm):

	FPS = 50
	STEPS_PER_FRAME = 80
	CAMERA_POSITION = (0,8,30)

	VEHICLE_OFFSET = (-1.05,-0.35,5)
	TM_X, TM_Z = (40,20)

	LINK1_PARAMS = ((0.8, 0.1,(0,0,0)),{'mass':1}) # ((length, radius, center), mass)
	LINK2_PARAMS = ((0.6,0.1,(0,0.7,0.2)),{'mass':1})

	Q1_FRICTION_COEFF = 0.02
	Q2_FRICTION_COEFF = 0.02

	WHEELS_TORQUE = 4.0
	MAX_SPEED = 2.0

	# arm controller
	q1_SP = 0.0 # set point
	R1_KP = 20.0 # controller proportional action
	R1_KD = 15.0 # controller derivative action

	q2_SP = 0.0
	R2_KP = 20.0
	R2_KD = 15.0

	def __init__(self):
		"""Constructor, calls the superclass constructor first"""
		VehicleWithArm.__init__(self)
		dispatcher.connect(self.on_pre_step, SIM_PRE_STEP_SIGNAL)

		self.q1_previous_error = 0.0
		self.q2_previous_error = 0.0

	def create_simulation(self):

		tm_x, tm_z = self.TM_X, self.TM_Z
		vertices = sinusoidal_heightfield(tm_x, tm_z, height_scale=0.7, frequency_x=0.5)
		faces = Trimesh.get_heightfield_faces(tm_x, tm_z)
		#vertices = constant_heightfield(tm_x, tm_z, height=0.0)
		#vertices = random_heightfield(tm_x, tm_z, 0.5)
		#shrink_factor = (1.0,1.0)
		#vertices = shrink_XZ_heightfield(vertices, shrink_factor)

		# set up the simulation parameters
		self.sim = Simulation(self.FPS, self.STEPS_PER_FRAME)
		self.sim.add_basic_simulation_objects()
		self.sim.add_axes()
		self.sim.add_trimesh_floor(vertices, faces, center=(-10,0,-10), color=(0.7,0.7,0.7))

		self.create_sim_objects()

		# add the graphic objects
		self.gAdapter.add_objects_list(self.sim.actors.values())
		self.sim.update_actors()

	def on_pre_step(self):
		try:
			time = self.sim.sim_time

			pos = self.sim.get_object(self.chassis).get_position()
			vel = self.sim.get_object(self.chassis).get_linear_velocity()
			q1 = self.sim.get_joint('r1').joint.angle
			q1p = self.sim.get_joint('r1').joint.angle_rate
			q2 = self.sim.get_joint('r2').joint.angle
			q2p = self.sim.get_joint('r2').joint.angle_rate

			if mut.length3(vel) < self.MAX_SPEED:
				wheels_torque = self.WHEELS_TORQUE
			else:
				wheels_torque = 0.0

			self.apply_torque_to_wheels(wheels_torque, wheels_torque)
			self.apply_friction(q1p, q2p)
			torque1, torque2 = self.get_arm_compensation(q1, q2)
			self.apply_torque_to_joints(torque1, torque2)

			print('%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e\t%.7e' %
				(time,pos[0],pos[1],pos[2],q1,torque1,q2,torque2,wheels_torque))

		except Exception as e:
			print('Exception when executing on_pre_step: %s' % str(e))

	def get_arm_compensation(self, q1, q2):
		"""Calculate the control torque with a PD controller"""
		time_step = self.sim.time_step
		error_q1 = (self.q1_SP - q1)
		error_q2 = (self.q2_SP - q2)

		error_q1_p = (error_q1 - self.q1_previous_error) / time_step
		error_q2_p = (error_q2 - self.q2_previous_error) / time_step

		torque1 = self.R1_KP * error_q1 + self.R1_KD * error_q1_p
		torque2 = self.R2_KP * error_q2 + self.R2_KD * error_q2_p

		self.q1_previous_error = error_q1
		self.q2_previous_error = error_q2

		return torque1, torque2

if __name__ == '__main__':
	sim_program = Example4()
	sim_program.start()

#===============================================================================
# def shrink_XZ_heightfield(vertices, factor=(1.0,1.0)):
#	"""
#	test
#	"""
#	new_vertices = []
#	for vertex in vertices:
#		new_vertices.append((vertex[0]/factor[0], vertex[1], vertex[2]/factor[1]))
#	return new_vertices
#===============================================================================