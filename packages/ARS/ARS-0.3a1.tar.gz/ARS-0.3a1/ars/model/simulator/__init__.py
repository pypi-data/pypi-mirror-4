from abc import ABCMeta, abstractmethod

import ars.exceptions as exc
import ars.graphics.adapters as gp
from ars.lib.pydispatch import dispatcher
import ars.model.collision.adapters as coll
import ars.model.physics.adapters as phs
import ars.model.robot.joints as jo
import ars.utils.geometry as gemut
import ars.utils.mathematical as mu


SIM_PRE_STEP_SIGNAL = 'simulation pre step'
SIM_POST_STEP_SIGNAL = 'simulation post step'
SIM_PRE_FRAME_SIGNAL = 'simulation pre frame'
SIM_POST_FRAME_SIGNAL = 'simulation post frame'


class Simulation:

	def __init__(self, FPS, STEPS_PF, do_debug=False):
		self._FPS = FPS
		self._DT = 1.0 / FPS
		self._STEPS_PF = STEPS_PF  # steps per frame
		self.paused = False
		self.sim_time = 0.0
		self.num_iter = 0
		self.num_frame = 0

		self._contact_group = None
		self._world = None
		self._space = None

		self._floor_geom = None

		self._debug = do_debug
		self._objects = {}
		self._joints = {}

		# stores functions to be called on each step of a specific frame.
		# 	e.g. addTorque
		self.all_frame_steps_callbacks = []

		self.coll_engine = coll.OdeEngine()
		self.phs_engine = phs.OdeEngine()

	def add_basic_simulation_objects(self):
		"""Create the basic simulation objects needed for physics and collision
		such as a contact group (holds temporary contact joints generated during
		collisions), a simulation 'world' (where physics objects are processed)
		and a collision space (the same thing for geoms and their
		intersections).

		"""
		self._contact_group = self.phs_engine.create_joint_group()
		self._world = self.phs_engine.create_world()
		self._space = coll.Space()

	def on_idle(self):
		self.num_frame += 1

		try:
			dispatcher.send(SIM_PRE_FRAME_SIGNAL) # before each visualization frame
		except Exception as e:
			print(e)

		self.perform_sim_steps_per_frame()

		try:
			dispatcher.send(SIM_POST_FRAME_SIGNAL) # after each visualization frame
		except Exception as e:
			print(e)

		# clear functions registered to be called in the steps of this past frame
		self.all_frame_steps_callbacks = []

		if self._debug:
			print(self.sim_time)
		self.update_actors()

	def perform_sim_steps_per_frame(self):

		time_step = self.time_step

		for i in range(self._STEPS_PF):

			# before each integration step of the physics engine
			try:
				# send the signal so subscribers do their stuff in time
				dispatcher.send(SIM_PRE_STEP_SIGNAL)
				# call all registered functions before each step of the next frame
				for callback_ in self.all_frame_steps_callbacks:
					callback_()
			except Exception as e:
				print(e)

			# Detect collisions and create contact joints
			coll_args = coll.NearCallbackArgs(self._world, self._contact_group)
			self._space.collide(coll_args)

			# step world sim
			self._world.step(time_step)
			self.sim_time += time_step
			self.num_iter += 1

			# Remove all contact joints
			self._contact_group.empty()

			# after each integration step of the physics engine
			try:
				dispatcher.send(SIM_POST_STEP_SIGNAL)
			except Exception as e:
				print(e)

	def update_actors(self):
		"""Update the position and rotation of each simulated object's
		corresponding actor"""
		for key_ in self._objects:
			try:
				if self._objects[key_].is_updatable():
					self._objects[key_].update_actor()

			except (ValueError, AttributeError) as err:
				print(err)

	@property
	def time_step(self):
		return self._DT / self._STEPS_PF

	@property
	def collision_space(self):
		return self._space

	def add_axes(self):
		gAxes = gp.Axes()
		name = 'axes'
		return self.add_object(SimulatedObject(name, actor=gAxes))

	def add_floor(self, normal=(0, 1, 0), dist=0, box_size=(5, 0.1, 5),
			box_center=(0, 0, 0), color=(0.2, 0.5, 0.5)):
		"""Create a plane geom to simulate a floor. It won't be used explicitly
		later (space object has a reference to it)"""
		# FIXME: the relation between ODE's definition of plane and the center
		# 	of the box
		self._floor_geom = self.phs_engine.create_plane_geom(self._space,
			normal, dist)
		# TODO: use normal parameter for orientation
		gFloor = gp.Box(box_size, box_center)
		gFloor.set_color(color)
		name = "floor"
		return self.add_object(SimulatedObject(name, actor=gFloor))

	def add_trimesh_floor(self, vertices, faces, center=(0, 0, 0),
			color=(0.2, 0.5, 0.5)):
		self._floor_geom = coll.Trimesh(self._space, vertices, faces, center)
		gFloor = gp.Trimesh(vertices, faces, center)
		gFloor.set_color(color)
		name = "floor"
		return self.add_object(SimulatedBody(name, actor=gFloor))

	def add_sphere(self, radius, center, mass=None, density=None):
		body = phs.Sphere(self._world, self._space, radius, mass, density)
		body.set_position(center)

		g_sphere = gp.Sphere(radius, center)
		name = "sphere"
		return self.add_object(SimulatedBody(name, body, g_sphere))

	def add_box(self, size, center, mass=None, density=None):
		body = phs.Box(self._world, self._space, size, mass, density)
		body.set_position(center)

		g_box = gp.Box(size, center)
		name = "box" + str(center)  # FIXME
		return self.add_object(SimulatedBody(name, body, g_box))

	def add_cylinder(self, length, radius, center, mass=None, density=None):
		body = phs.Cylinder(self._world, self._space, length, radius, mass, density)
		body.set_position(center)

		g_cylinder = gp.Cylinder(length, radius, center)
		name = "cylinder"
		return self.add_object(SimulatedBody(name, body, g_cylinder))

	def add_capsule(self, length, radius, center, mass=None, density=None):
		body = phs.Capsule(self._world, self._space, length, radius, mass, density)
		body.set_position(center)

		g_capsule = gp.Capsule(length, radius, center)
		name = "capsule"
		return self.add_object(SimulatedBody(name, body, g_capsule))

	@property
	def actors(self):
		"""Returns a dictionary with each object actor indexed by its name"""
		actors = {}
		for key_ in self._objects:
			actor = self._objects[key_].actor
			if actor:
				actors[key_] = actor
		return actors

	def add_object(self, sim_object):
		"""Adds an object to the internal dictionary of simulated ones"""
		name = sim_object.get_name()
		if (name in self._objects.keys()) and name:
			name = name + '/' + str(sim_object.body)
			sim_object.set_name(name)
		self._objects[name] = sim_object
		return name

	def add_joint(self, sim_joint):
		name = sim_joint.get_name()
		if (name in self._joints.keys()) and name:
			name = name + '/' + str(sim_joint.joint)
			sim_joint.set_name(name)
		self._joints[name] = sim_joint
		return name

	def get_object(self, name):
		return self._objects[name]

	def get_joint(self, name):
		return self._joints[name]

	#==========================================================================
	# Add joints
	#==========================================================================

	def add_fixed_joint(self, obj1, obj2):
		body1 = obj1.body
		body2 = obj2.body
		f_joint = jo.Fixed(self._world, body1, body2)
		return self.add_joint(SimulatedJoint(joint=f_joint))

	def add_rotary_joint(self, name, obj1, obj2, anchor, axis):
		"""Adds a rotary joint between obj1 and obj2, at the specified anchor
		and with the given axis. If anchor = None, it will be set equal to the
		position of obj2"""
		body1 = obj1.body
		body2 = obj2.body
		if not anchor:
			anchor = obj2.get_position()

		r_joint = jo.Rotary(self._world, body1, body2, anchor, axis)
		return self.add_joint(SimulatedJoint(name, r_joint))

	def add_universal_joint(self, obj1, obj2, anchor, axis1, axis2):
		body1 = obj1.body
		body2 = obj2.body
		u_joint = jo.Universal(self._world, body1, body2, anchor, axis1, axis2)
		return self.add_joint(SimulatedJoint(joint=u_joint))

	def add_ball_socket_joint(self, name, obj1, obj2, anchor):
		"""Adds a "ball and socket" joint between obj1 and obj2, at the
		specified anchor. If anchor = None, it will be set equal to the
		position of obj2."""
		body1 = obj1.body
		body2 = obj2.body
		if not anchor:
			anchor = obj2.get_position()

		bs_joint = jo.BallSocket(self._world, body1, body2, anchor)
		return self.add_joint(SimulatedJoint(name, bs_joint))


class SimulatedObject:
	__metaclass__ = ABCMeta

	_updatable = False

	def __init__(self, name, actor=None):
		if name:
			self._name = name
		else:
			self._name = str(self)
		self._actor = actor

	#==========================================================================
	# Getters and setters
	#==========================================================================

	def get_name(self):
		return self._name

	def set_name(self, name):
		self._name = name

	@property
	def actor(self):
		return self._actor

	def has_actor(self):
		return not self._actor is None

	def is_updatable(self):
		return self.has_actor() and self._updatable


class SimulatedPhysicsObject(SimulatedObject):
	__metaclass__ = ABCMeta

	_updatable = True

	def rotate(self, axis, angle):
		"""Rotate the object by applying a rotation matrix defined by the given
		axis and angle"""
		rot_now = mu.matrix_as_3x3_tuples(self.get_rotation())
		rot_to_apply = mu.matrix_as_3x3_tuples(gemut.calc_rotation_matrix(axis,
			angle))
		# Matrix (of the rotation to apply)
		# multiplies from the LEFT the actual one
		rot_final = mu.matrix_as_tuple(mu.matrix3_multiply(rot_to_apply, rot_now))
		self.set_rotation(rot_final)

	@abstractmethod
	def offset_by_position(self, offset_pos):
		pass

	def offset_by_object(self, object_):
		offset_pos = object_.get_position()
		self.offset_by_position(offset_pos)

	def update_actor(self):
		"""If there is no actor, it won't do anything"""
		if self.has_actor() and self._updatable:
			pos = self.get_position()
			rot = self.get_rotation()
			self._actor.update_position_rotation(pos, rot)

	@abstractmethod
	def get_position(self):
		pass

	@abstractmethod
	def set_position(self, position):
		pass

	@abstractmethod
	def get_rotation(self):
		pass

	@abstractmethod
	def set_rotation(self, rot_matrix):
		pass


class SimulatedBody(SimulatedPhysicsObject):

	def __init__(self, name, body=None, actor=None, geom=None):
		super(SimulatedBody, self).__init__(name, actor)
		self._body = body
		self._geom = geom  # we might need it in the future

	def offset_by_position(self, offset_pos):
		pos = self._body.get_position()
		new_pos = mu.add3(offset_pos, pos)
		self.set_position(new_pos)

	#def has_body(self):
	#	return not self._body is None

	#==========================================================================
	# Getters and setters
	#==========================================================================

	@property
	def body(self):
		return self._body

	def get_position(self):
		return self._body.get_position()

	def set_position(self, position):
		self._body.set_position(position)

	def get_rotation(self):
		return self._body.get_rotation()

	def set_rotation(self, rot_matrix):
		self._body.set_rotation(rot_matrix)

	def get_linear_velocity(self):
		return self._body.get_linear_velocity()

	def get_angular_velocity(self):
		return self._body.get_angular_velocity()

class SimulatedJoint(SimulatedPhysicsObject):

	def __init__(self, name=None, joint=None, actor=None):
		super(SimulatedJoint, self).__init__(name, actor)
		self._joint = joint

	def offset_by_position(self, offset_pos):
		raise NotImplementedError()

	#==========================================================================
	# Dynamic and kinematic interaction
	#==========================================================================

	def add_torque(self, torque):
		try:
			self._joint.add_torque(torque)
		except Exception as ex:
			print(ex)

	#==========================================================================
	# Getters and setters
	#==========================================================================

	@property
	def joint(self):
		return self._joint

	def get_position(self):
		# It is necessary to have this method, even if it's not implemented
		raise NotImplementedError()

	def set_position(self, position):
		# It is necessary to have this method, even if it's not implemented
		raise NotImplementedError()

	def get_rotation(self):
		# It is necessary to have this method, even if it's not implemented
		raise NotImplementedError()

	def set_rotation(self, rot_matrix):
		# It is necessary to have this method, even if it's not implemented
		raise NotImplementedError()
