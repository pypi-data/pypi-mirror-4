from abc import ABCMeta

import ode

from ...lib.pydispatch import dispatcher
from ..collision import adapters as shapes

from . import base, signals


class OdeWorld(base.World):
	def __init__(self, gravity=(0.0,-9.81,0.0), ERP=0.8, CFM=1E-10, *args,
			**kwargs):
		"""Create an ODE world object.

		:param gravity: Gravity acceleration.
		:type gravity: 3 floats tuple.
		:param ERP: Error Reduction Parameter.
		:type ERP: float.
		:param CFM: Constraint Force Mixing.
		:type CFM: float.

		"""
		super(OdeWorld, self).__init__(gravity, *args, **kwargs)
		self._inner_object = _create_ode_world(gravity, ERP, CFM)

	@property
	def gravity(self):
		return self._inner_object.getGravity()

	def step(self, time_step):
		dispatcher.send(signals.WORLD_PRE_STEP, sender=self)
		self._inner_object.step(time_step)
		dispatcher.send(signals.WORLD_POST_STEP, sender=self)


class OdeEngine(base.Engine):
	"""Adapter to the ODE physics engine"""

	world_class = OdeWorld

#	def __init__(self):
#		pass

	@staticmethod
	def create_joint_group():
		return ode.JointGroup()

	@staticmethod
	def create_plane_geom(space, normal, dist):
		return ode.GeomPlane(space.inner_object, normal, dist)


class OdeBody:
	__metaclass__ = ABCMeta

	def __init__(self, world, space, mass=None, density=None, *args, **kwargs):
		self._inner_object = None

	#==========================================================================
	# Getters and setters
	#==========================================================================

	def get_position(self):
		"""Get the position of the body.

		:return: position
		:rtype: 3-sequence of floats

		"""
		return self._inner_object.getPosition()

	def get_linear_velocity(self):
		return self._inner_object.getLinearVel()

	def get_rotation(self):
		"""Get the orientation of the body.

		:return: rotation matrix
		:rtype: 9-sequence of floats

		"""
		return self._inner_object.getRotation()

	def get_angular_velocity(self):
		return self._inner_object.getAngularVel()

	def get_mass(self):
		return self._inner_object.getMass().mass

	def get_center_of_gravity(self):
		return self._inner_object.getMass().c

	def get_inertia_tensor(self):
		return self._inner_object.getMass().I

	def set_position(self, pos):
		"""Set the position of the body.

		Sends :data:`signals.BODY_PRE_SET_POSITION` and
		:data:`signals.BODY_POST_SET_POSITION`.

		:param pos: position
		:type pos: 3-sequence of floats

		"""
		dispatcher.send(signals.BODY_PRE_SET_POSITION, sender=self)
		self._inner_object.setPosition(pos)
		dispatcher.send(signals.BODY_POST_SET_POSITION, sender=self)

	def set_rotation(self, rot):
		"""Set the orientation of the body.

		Sends :data:`signals.BODY_PRE_SET_ROTATION` and
		:data:`signals.BODY_POST_SET_ROTATION`.

		:param rot: rotation matrix
		:type rot: 9-sequence of floats

		"""
		dispatcher.send(signals.BODY_PRE_SET_ROTATION, sender=self)
		self._inner_object.setRotation(rot)
		dispatcher.send(signals.BODY_POST_SET_ROTATION, sender=self)


class Capsule(OdeBody, base.Capsule):
	def __init__(self, world, space, length, radius, mass=None, density=None):
		"""create capsule body (aligned along the z-axis so that it matches the
		Geom created below,	which is aligned along the Z-axis by default)"""
		OdeBody.__init__(self, world, space, mass, density)
		base.Capsule.__init__(self, length, radius, mass, density)

		body = _create_ode_capsule(world, length, radius, mass, density)
		geom = shapes.Capsule(space, length, radius)
		self._inner_object = body
		self.attach_geom(geom)


class Cylinder(OdeBody, base.Cylinder):
	def __init__(self, world, space, length, radius, mass=None, density=None):
		"""create cylinder body (aligned along the z-axis so that it matches
		the Geom created below,	which is aligned along the Z-axis by default)"""
		OdeBody.__init__(self, world, space, mass, density)
		base.Cylinder.__init__(self, length, radius, mass, density)

		body = _create_ode_cylinder(world, length, radius, mass, density)
		geom = shapes.Cylinder(space, length, radius)
		self._inner_object = body
		self.attach_geom(geom)


class Box(OdeBody, base.Box):
	def __init__(self, world, space, size, mass=None, density=None):
		OdeBody.__init__(self, world, space, mass, density)
		base.Box.__init__(self, size, mass, density)

		body = _create_ode_box(world, size, mass, density)
		geom = shapes.Box(space, size)
		self._inner_object = body
		self.attach_geom(geom)


class Sphere(OdeBody, base.Sphere):
	def __init__(self, world, space, radius, mass=None, density=None):
		OdeBody.__init__(self, world, space, mass, density)
		base.Sphere.__init__(self, radius, mass, density)

		body = _create_ode_sphere(world, radius, mass, density)
		geom = shapes.Sphere(space, radius)
		self._inner_object = body
		self.attach_geom(geom)

#==============================================================================
# Private functions
#==============================================================================


def _create_ode_world(gravity=(0.0,-9.81,0.0), ERP=0.8, CFM=1E-10):
	"""Create an ODE world object"""
	world = ode.World()
	world.setGravity(gravity)
	world.setERP(ERP)
	world.setCFM(CFM)
	return world


def _create_ode_capsule(world, length, radius, mass=None, density=None):

	capsule_direction = 3  # z-axis
	body = ode.Body(world._inner_object)

	if mass is not None:
		m = ode.Mass()
		m.setCapsuleTotal(mass, capsule_direction, radius, length)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setCapsule(density, capsule_direction, radius, length)
		body.setMass(m)

	# set parameters for drawing the body
	# TODO: delete this, because it is related to the original implementation
	body.shape = "capsule"
	body.length = length
	body.radius = radius

	return body


def _create_ode_cylinder(world, length, radius, mass=None, density=None):
	cylinderDirection = 3  # Z-axis
	body = ode.Body(world._inner_object)

	if mass is not None:
		m = ode.Mass()
		m.setCylinderTotal(mass, cylinderDirection, radius, length)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setCylinder(density, cylinderDirection, radius, length)
		body.setMass(m)

	return body


def _create_ode_box(world, size, mass=None, density=None):
	body = ode.Body(world._inner_object)

	if mass is not None:
		m = ode.Mass()
		m.setBoxTotal(mass, *size)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setBox(density, *size)
		body.setMass(m)

	return body


def _create_ode_sphere(world, radius, mass=None, density=None):
	body = ode.Body(world._inner_object)

	if mass is not None:
		m = ode.Mass()
		m.setSphereTotal(mass, radius)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setSphere(density, radius)
		body.setMass(m)

	return body
