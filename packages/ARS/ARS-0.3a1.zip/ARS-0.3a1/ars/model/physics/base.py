from abc import ABCMeta, abstractmethod


class Engine:
	__metaclass__ = ABCMeta

#	@abstractmethod
#	def __init__(self):
#		raise NotImplementedError()


class Body:
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		self._inner_object = None
		self._attached_geom = None

	def attach_geom(self, geom):
		geom.attach_body(self)
		self._attached_geom = geom

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
		raise NotImplementedError()

	@abstractmethod
	def get_linear_velocity(self):
		raise NotImplementedError()

	@abstractmethod
	def get_rotation(self):
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
		raise NotImplementedError()

	@abstractmethod
	def set_rotation(self, rot):
		raise NotImplementedError()


class Box(Body):
	__metaclass__ = ABCMeta

	def __init__(self, size, position, rotation=None):
		super(Box, self).__init__()


class Cone(Body):
	__metaclass__ = ABCMeta

	def __init__(self, height, radius, center, rotation=None):
		super(Cone, self).__init__()


class Sphere(Body):
	__metaclass__ = ABCMeta

	def __init__(self, radius, center, rotation=None):
		super(Sphere, self).__init__()


class Cylinder(Body):
	__metaclass__ = ABCMeta

	def __init__(self, length, radius, center, rotation=None):
		super(Cylinder, self).__init__()


class Capsule(Body):
	__metaclass__ = ABCMeta

	def __init__(self, length, radius, center, rotation=None):
		super(Capsule, self).__init__()
