from abc import ABCMeta, abstractmethod, abstractproperty

from ... import exceptions as exc
from ...lib.pydispatch import dispatcher
from ...utils import mathematical as mut

from . import signals


class Engine:
	__metaclass__ = ABCMeta

#	@abstractmethod
#	def __init__(self):
#		raise NotImplementedError()


class World:
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, gravity, *args, **kwargs):
		self._inner_object = None

	@property
	def inner_object(self):
		return self._inner_object

	@abstractproperty
	def gravity(self):
		raise NotImplementedError()

	@abstractmethod
	def step(self, time_step):
		"""Subclasses implementing this method must send the corresponding
		signals, defined in :mod:`ars.model.physics.signals`.

		"""
		raise NotImplementedError()


class Body:
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, mass=None, density=None, pos=None, rot=None,
			*args, **kwargs):

		if mass is not None:
			if density is not None:
				raise exc.ArsError('Both mass and density arguments were given')

		self._inner_object = None
		self._attached_geom = None

		self._saved_linear_vel = None
		self._saved_angular_vel = None

	def attach_geom(self, geom):
		geom.attach_body(self)
		self._attached_geom = geom
		dispatcher.send(signals.BODY_POST_ATTACH_GEOM, sender=self)

	#==========================================================================
	# Calculations
	#==========================================================================

	def calc_translation_kinetic_energy(self):
		r"""Calculate the kinetic energy of the body due to translational
		movement.

		.. math::
			E_{kt} = \frac{1}{2} m v^2
			  = \frac{1}{2} m \cdot v^\top v

		:return: kinetic energy
		:rtype: float

		"""
		mass = self.get_mass()
		linear_vel = self.get_linear_velocity()
		return mass * mut.dot_product(linear_vel, linear_vel) / 2.0

	def calc_rotation_kinetic_energy(self):
		r"""Calculate the kinetic energy of the body due to rotational
		movement.

		.. math::
			E_{kr} = \frac{1}{2} I \omega^2 =
			  \frac{1}{2} \omega^\top \mathbf{I} \omega

		:return: kinetic energy
		:rtype: float

		"""
		It = self.get_inertia_tensor()
		angular_vel = self.get_angular_velocity()
		return mut.vector_matrix_vector(angular_vel, It) / 2.0

	def calc_potential_energy(self, gravity):
		r"""Calculate the potential energy of the body due to its position
		(`x`) and the gravitational acceleration (`g`).

		.. math::
			E_p &= m \cdot g \cdot h = - m \cdot g^\top x

		:param gravity: gravitational acceleration vector
		:type gravity: tuple of 3 floats
		:return: potential energy
		:rtype: float

		"""
		mass = self.get_mass()
		return -mass * mut.dot_product(gravity, self.get_position())

	#==========================================================================
	# Getters and setters
	#==========================================================================

	@property
	def inner_object(self):
		return self._inner_object

	def get_attached_geom(self):
		return self._attached_geom

	@abstractmethod
	def get_position(self):
		"""Get the position of the body.

		:return: position
		:rtype: 3-sequence of floats

		"""
		raise NotImplementedError()

	@abstractmethod
	def get_linear_velocity(self):
		raise NotImplementedError()

	@abstractmethod
	def get_rotation(self):
		"""Get the orientation of the body.

		:return: rotation matrix
		:rtype: 9-sequence of floats

		"""
		raise NotImplementedError()

	@abstractmethod
	def get_angular_velocity(self):
		raise NotImplementedError()

	@abstractmethod
	def get_mass(self):
		raise NotImplementedError()

	@abstractmethod
	def get_center_of_gravity(self):
		raise NotImplementedError()

	@abstractmethod
	def get_inertia_tensor(self):
		raise NotImplementedError()

	@abstractmethod
	def set_position(self, pos):
		"""Set the position of the body.

		Sends :data:`signals.BODY_PRE_SET_POSITION` and
		:data:`signals.BODY_POST_SET_POSITION`.

		:param pos: position
		:type pos: 3-sequence of floats

		"""
		raise NotImplementedError()

	@abstractmethod
	def set_rotation(self, rot):
		"""Set the orientation of the body.

		Sends :data:`signals.BODY_PRE_SET_ROTATION` and
		:data:`signals.BODY_POST_SET_ROTATION`.

		:param rot: rotation matrix
		:type rot: 9-sequence of floats

		"""
		raise NotImplementedError()

	def save_velocities(self):
		"""Retrieve the actual velocities (linear and angular) of the body and
		save them.

		"""
		self._saved_linear_vel = self.get_linear_velocity()
		self._saved_angular_vel = self.get_angular_velocity()

	def get_saved_velocities(self):
		"""Return last saved velocities (linear and angular)."""
		return self._saved_linear_vel, self._saved_angular_vel


class Box(Body):
	__metaclass__ = ABCMeta

	def __init__(self, size, *args, **kwargs):
		super(Box, self).__init__(*args, **kwargs)
		self._size = size

	@property
	def size(self):
		return self._size


class Cone(Body):
	__metaclass__ = ABCMeta

	def __init__(self, height, radius, *args, **kwargs):
		super(Cone, self).__init__(*args, **kwargs)
		self._height = height
		self._radius = radius

	@property
	def height(self):
		return self._height

	@property
	def radius(self):
		return self._radius


class Sphere(Body):
	__metaclass__ = ABCMeta

	def __init__(self, radius, *args, **kwargs):
		super(Sphere, self).__init__(*args, **kwargs)
		self._radius = radius

	@property
	def radius(self):
		return self._radius


class Cylinder(Body):
	__metaclass__ = ABCMeta

	def __init__(self, length, radius, *args, **kwargs):
		super(Cylinder, self).__init__(*args, **kwargs)
		self._length = length
		self._radius = radius

	@property
	def length(self):
		return self._length

	@property
	def radius(self):
		return self._radius


class Capsule(Body):
	__metaclass__ = ABCMeta

	def __init__(self, length, radius, *args, **kwargs):
		super(Capsule, self).__init__(*args, **kwargs)
		self._length = length
		self._radius = radius

	@property
	def length(self):
		return self._length

	@property
	def radius(self):
		return self._radius
