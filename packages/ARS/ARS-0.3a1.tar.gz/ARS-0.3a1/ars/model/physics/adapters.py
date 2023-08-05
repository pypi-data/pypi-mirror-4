import ode

import ars.exceptions as exc
import ars.model.collision.adapters as shapes

import base


class OdeEngine(base.Engine):
	"""Adapter to the ODE physics engine"""

#	def __init__(self):
#		pass

	@staticmethod
	def create_joint_group():
		return ode.JointGroup()
	
	@staticmethod
	def create_world(gravity=(0.0,-9.81,0.0), ERP=0.8, CFM=1E-10):
		"""Create an ODE world object"""
		world = ode.World()
		world.setGravity(gravity)
		world.setERP(ERP)
		world.setCFM(CFM)
		return world

	@staticmethod
	def create_plane_geom(space, normal, dist):
		return ode.GeomPlane(space.inner_object, normal, dist)


class OdeBody:

	def __init__(self):
		self._inner_object = None

	#==========================================================================
	# Getters and setters
	#==========================================================================

	def get_position(self):
		return self._inner_object.getPosition()

	def get_linear_velocity(self):
		return self._inner_object.getLinearVel()

	def get_rotation(self):
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
		self._inner_object.setPosition(pos)

	def set_rotation(self, rot):
		self._inner_object.setRotation(rot)


class Capsule(OdeBody, base.Capsule):
	def __init__(self, world, space, length, radius, mass=None, density=None):
		"""create capsule body (aligned along the z-axis so that it matches the
		Geom created below,	which is aligned along the Z-axis by default)"""
		super(Capsule, self).__init__()

		if mass is not None:
			if density is not None:
				raise exc.ArsError('Both mass and density arguments were given')

		self._length = length
		self._radius = radius

		body = _create_ode_capsule(world, length, radius, mass, density)
		geom = shapes.Capsule(space, length, radius)
		self._inner_object = body
		self.attach_geom(geom)

	@property
	def length(self):
		return self._length

	@property
	def radius(self):
		return self._radius

class Cylinder(OdeBody, base.Cylinder):
	def __init__(self, world, space, length, radius, mass=None, density=None):
		"""create cylinder body (aligned along the z-axis so that it matches
		the Geom created below,	which is aligned along the Z-axis by default)"""
		super(Cylinder, self).__init__()

		if mass is not None:
			if density is not None:
				raise exc.ArsError('Both mass and density arguments were given')

		self._length = length
		self._radius = radius

		body = _create_ode_cylinder(world, length, radius, mass, density)
		geom = shapes.Cylinder(space, length, radius)
		self._inner_object = body
		self.attach_geom(geom)

	@property
	def length(self):
		return self._length

	@property
	def radius(self):
		return self._radius

class Box(OdeBody, base.Box):
	def __init__(self, world, space, size, mass=None, density=None):
		super(Box, self).__init__()

		if mass is not None:
			if density is not None:
				raise exc.ArsError('Both mass and density arguments were given')

		self._size = size

		body = _create_ode_box(world, size, mass, density)
		geom = shapes.Box(space, size)
		self._inner_object = body
		self.attach_geom(geom)

	@property
	def size(self):
		return self._size

class Sphere(OdeBody, base.Sphere):
	def __init__(self, world, space, radius, mass=None, density=None):
		super(Sphere, self).__init__()

		if mass is not None:
			if density is not None:
				raise exc.ArsError('Both mass and density arguments were given')

		self._radius = radius

		body = _create_ode_sphere(world, radius, mass, density)
		geom = shapes.Sphere(space, radius)
		self._inner_object = body
		self.attach_geom(geom)

	@property
	def radius(self):
		return self._radius

#==============================================================================
# Private functions
#==============================================================================

def _create_ode_capsule(world, length, radius, mass=None, density=None):

	capsule_direction = 3  # z-axis
	body = ode.Body(world)

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
	body = ode.Body(world)

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
	body = ode.Body(world)

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
	body = ode.Body(world)

	if mass is not None:
		m = ode.Mass()
		m.setSphereTotal(mass, radius)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setSphere(density, radius)
		body.setMass(m)

	return body
