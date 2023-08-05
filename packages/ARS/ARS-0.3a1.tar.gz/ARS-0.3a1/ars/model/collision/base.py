from abc import ABCMeta, abstractmethod

import ars.exceptions as exc

class Engine:
	__metaclass__ = ABCMeta

#	@abstractmethod
#	def __init__(self):
#		raise NotImplementedError()


class Space:
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		self._inner_object = None

	@property
	def inner_object(self):
		return self._inner_object

	@abstractmethod
	def collide(self, args, callback):
		raise NotImplementedError()


class Geom:
	"""Encapsules a geometry object"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		self._inner_object = None
		self._attached_body = None

	@abstractmethod
	def attach_body(self, body):
		self._attached_body = body

	#==========================================================================
	# Getters and setters
	#==========================================================================
	@property
	def inner_object(self):
		return self._inner_object

	def get_attached_body(self):
		return self._attached_body

	@abstractmethod
	def get_position(self):
		pass

	@abstractmethod
	def get_rotation(self):
		pass

	@abstractmethod
	def set_position(self, pos):
		pass

	@abstractmethod
	def set_rotation(self, rot):
		pass


class Ray(Geom):
	"""
	Ray aligned along the Z-axis by default.
	"A ray is different from all the other geom classes in that it does not
	represent a solid object. It is an infinitely thin line that starts from
	the geom's position and	extends in the direction of the geom's local
	Z-axis." (ODE Wiki Manual)
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, length):
		super(Ray, self).__init__()
		self._last_contact = None
		self._closer_contact = None

	@abstractmethod
	def get_length(self):
		pass

	@abstractmethod
	def set_length(self, length):
		pass

	def get_last_contact(self):
		"""Returns the contact object corresponding to the last collision of
		the ray with another geom. Note than in each simulation step, several
		collisions may occur, one for each intersection geom (in ODE).
		The object returned may or may not be the same returned by
		`get_closer_contact`.
		"""
		return self._last_contact

	def get_closer_contact(self):
		"""Returns the contact object corresponding to the collision closest to
		the ray's origin.
		It may or may not be the same object returned by `get_last_contact`.
		"""
		return self._closer_contact

	def set_last_contact(self, last_contact):
		"""Sets the last contact object with which the ray collided. It also
		checks if `last_contact` is closer than the previously existing one.
		The result can be obtained with the `get_closer_contact` method.
		"""
		if self._last_contact is None:
			self._closer_contact = last_contact
		else:
			if self._last_contact.depth > last_contact.depth:
				self._closer_contact = last_contact
		self._last_contact = last_contact

	def clear_last_contact(self):
		self._last_contact = None

	def clear_closer_contact(self):
		self._closer_contact = None

	def clear_contacts(self):
		self.clear_last_contact()
		self.clear_closer_contact()


class Trimesh(Geom):

	@abstractmethod
	def __init__(self, space, vertices, faces, center):
		super(Trimesh, self).__init__()

	@staticmethod
	def get_heightfield_faces(num_x, num_z):
		"""Creates the faces corresponding to a heightfield size 'num_x' by
		'num_z'. Faces are triangular, so each is composed by 3 vertices."""

		# index of each square is calculated because it is needed to define faces
		indices = []

		for x in range(num_x):
			indices_x = []
			for z in range(num_z):
				indices_x.insert(z, num_z * x + z)
			indices.insert(x, indices_x)

		# faces = [(1a,1b,1c), (2a,2b,2c), ...]
		faces = []

		for x in range(num_x - 1):
			for z in range(num_z - 1):

				zero = indices[x][z]			# top-left corner
				one = indices[x][z + 1]			# bottom-left
				two = indices[x + 1][z]			# top-right
				three = indices[x + 1][z + 1] 	# bottom-right

				# there are two face types for each square
				# contiguous squares must have different face types
				face_type = zero
				if num_z % 2 == 0:
					face_type += 1

				# there are 2 faces per square
				if face_type % 2 == 0:
					face1 = (zero, three, two)
					face2 = (zero, one, three)
				else:
					face1 = (zero, one, two)
					face2 = (one, three, two)

				faces.append(face1)
				faces.append(face2)

		return faces

	@staticmethod
	def swap_faces_indices(faces):
		"""Faces had to change their indices to work with ODE. With the initial
		get_faces, the normal to the triangle defined by the 3 vertices pointed
		(following the right-hand rule) downwards. Swapping the third with the
		first index, now the triangle normal pointed upwards."""

		new_faces = []
		for face in faces:
			new_faces.append((face[2], face[1], face[0]))
		return new_faces

	#==========================================================================
	# def attach_body(self, body):
	#	raise exc.ArsError('Trimesh shapes are not yet allowed to have a body attached')
	#
	# def get_attached_body(self):
	#	raise exc.ArsError('Trimesh shapes are not yet allowed to have a body attached')
	#==========================================================================


class Terrain(Geom):
	__metaclass__ = ABCMeta

#==============================================================================
# Basic Shapes
#==============================================================================


class BasicShape(Geom):
	"""Abstract class from whom every solid object's shape derive"""
	__metaclass__ = ABCMeta


class Box(BasicShape):
	"""Box shape, aligned along the X, Y and Z axii by default"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, size):
		super(Box, self).__init__()


class Sphere(BasicShape):
	"""Spherical shape"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, radius):
		super(Sphere, self).__init__()


class Capsule(BasicShape):
	"""Capsule shape, aligned along the Z-axis by default"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, length, radius):
		super(Capsule, self).__init__()


class Cylinder(BasicShape):
	"""Cylinder shape, aligned along the Z-axis by default"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, length, radius):
		super(Cylinder, self).__init__()


class Plane(BasicShape):
	"""Plane, different from a box"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, normal, dist):
		super(Plane, self).__init__()


class Cone(BasicShape):
	"""Cone"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		super(Cone, self).__init__()


class RayContactData:
	"""Contact information of a collision between `ray` and `shape`"""

	def __init__(self, ray=None, shape=None, position=None, normal=None, depth=None):
		# -position: point at which the ray intersects the surface of the other
		# 	shape/geom.
		# -normal: surface normal of the other geom at the contact point.
		# -depth: distance from the start of the ray to the contact point.
		# 	TODO: is it true?
		self.ray = ray
		self.shape = shape
		self.position = position
		self.normal = normal
		self.depth = depth


class NearCallbackArgs:
	"""Class to encapsulate args passed to the `near_callback` function"""

	def __init__(self, world=None, contact_group=None, ignore_connected=True):
		self.world = world
		self.contact_group = contact_group
		self.ignore_connected = ignore_connected
