from abc import ABCMeta

import ode

import ars.exceptions as exc

import ars.model.collision.base as base


class OdeEngine(base.Engine):
	"""Adapter to the ODE collision engine"""

#	def __init__(self):
#		pass

	#==========================================================================
	# Functions and methods not overriding base class functions and methods
	#==========================================================================

	@staticmethod
	def near_callback(args, geom1, geom2):
		"""Callback function for the collide() method (in ODE). This function
		checks if the given geoms do collide and creates contact joints (c_joint)
		if they do, except if they are connected."""

		# Contact joint parameters:
		# 	-bounce: default=0.2
		# 	-mu: default=500.
		# 		very slippery 0-5, normal 50-500, very sticky 5000
		c_joint_bounce = 0.2
		c_joint_mu = 500

		world = args.world
		contact_group = args.contact_group
		ray_geom = None
		other_geom = None

		if args.ignore_connected and OdeEngine.are_geoms_connected(geom1,
			geom2):
			return

		#======================================================================
		# Ray's special case
		#======================================================================
		if OdeEngine.is_ray(geom1):
			if OdeEngine.is_ray(geom2):
				print('Weird, ODE says two rays may collide. '
					  'That case is not handled.')
				return
			else:
				ray_geom = geom1
				other_geom = geom2

		elif OdeEngine.is_ray(geom2):
			ray_geom = geom2
			other_geom = geom1

		#======================================================================
		# create contact joints
		#======================================================================
		# check if the objects collide
		contacts = ode.collide(geom1, geom2)
		for c in contacts:

			if ray_geom is not None:
				OdeEngine.handle_ray_collision(ray_geom, other_geom, c)
			else:  # we create a ContactJoint only if both geoms are not rays
				# set contact parameters
				c.setBounce(c_joint_bounce)
				c.setMu(c_joint_mu)
				# create contact joints
				j = ode.ContactJoint(world, contact_group, c)
				j.attach(geom1.getBody(), geom2.getBody())

	@staticmethod
	def are_geoms_connected(geom1, geom2):
		"""Are `geom1` and `geom2` connected (through the bodies they are
		attached to)?
		"""
		return ode.areConnected(geom1.getBody(), geom2.getBody())

	@staticmethod
	def is_ray(geom):
		"""Is `geom` a ray?"""
		return isinstance(geom, ode.GeomRay)

	@staticmethod
	def handle_ray_collision(ray, other_geom, contact):
		ray_pos = ray.getPosition()
		(pos, normal, depth, geom1, geom2) = contact.getContactGeomParams()
		ray_contact = base.RayContactData(
			ray, other_geom, ray_pos, normal, depth)  # distance = depth
		try:
			ray.outer_object.set_last_contact(ray_contact)
		except AttributeError:
			print("`ray` has no attribute `outer_object` ")
		except Exception:
			print("Ray's encapsulating object's last_contact attribute could not be set")


class Space(base.Space):
	def __init__(self):
		# ode.SimpleSpace() is the same as ode.Space(space_type=0)
		self._inner_object = ode.SimpleSpace()

	def collide(self, args, callback=None):
		if callback is None:
			self._inner_object.collide(args, OdeEngine.near_callback)
		else:
			self._inner_object.collide(args, callback)


class OdeGeom(base.Geom):

	def attach_body(self, body):
		super(OdeGeom, self).attach_body(body)
		self._inner_object.setBody(body.inner_object)

	#==========================================================================
	# Getters and setters
	#==========================================================================

	def get_position(self):
		return self._inner_object.getPosition()

	def get_rotation(self):
		return self._inner_object.getRotation()

	def set_position(self, pos):
		self._inner_object.setPosition(pos)

	def set_rotation(self, rot):
		self._inner_object.setRotation(rot)


class Ray(OdeGeom, base.Ray):

	def __init__(self, space, length):
		OdeGeom.__init__(self)
		base.Ray.__init__(self, space, length)
		self._inner_object = ode.GeomRay(space.inner_object, length)
		self._inner_object.outer_object = self  # the encapsulating object

	def get_length(self):
		return self._inner_object.getLength()

	def set_length(self, length):
		self._inner_object.setLength(length)


class Trimesh(OdeGeom, base.Trimesh):

	def __init__(self, space, vertices, faces, center):
		OdeGeom.__init__(self)
		base.Trimesh.__init__(self, space, vertices, faces, center)

		tm_data = ode.TriMeshData()
		tm_data.build(vertices, faces)
		self._inner_object = ode.GeomTriMesh(tm_data, space.inner_object)
		self._inner_object.setPosition(center)


class OdeBasicShape(OdeGeom):
	__metaclass__ = ABCMeta


class Box(OdeBasicShape, base.Box):
	"""Box shape, aligned along the X, Y and Z axii by default"""

	def __init__(self, space, size):
		OdeBasicShape.__init__(self)
		base.Box.__init__(self, space, size)

		self._inner_object = ode.GeomBox(space.inner_object, lengths=size)


class Sphere(OdeBasicShape, base.Sphere):
	"""Spherical shape"""

	def __init__(self, space, radius):
		OdeBasicShape.__init__(self)
		base.Sphere.__init__(self, space, radius)

		self._inner_object = ode.GeomSphere(space.inner_object, radius)


class Capsule(OdeBasicShape, base.Capsule):
	"""Capsule shape, aligned along the Z-axis by default"""

	def __init__(self, space, length, radius):
		# GeomCCylinder: Capped Cylinder
		OdeBasicShape.__init__(self)
		base.Capsule.__init__(self, space, length, radius)

		self._inner_object = ode.GeomCCylinder(
			space.inner_object, radius, length)


class Cylinder(OdeBasicShape, base.Cylinder):
	"""Cylinder shape, aligned along the Z-axis by default"""

	def __init__(self, space, length, radius):
		OdeBasicShape.__init__(self)
		base.Cylinder.__init__(self, space, length, radius)

		self._inner_object = ode.GeomCylinder(
			space.inner_object, radius, length)


class Plane(OdeBasicShape, base.Plane):
	"""Plane, different from a box"""

	def __init__(self, space, normal, dist):
		OdeBasicShape.__init__(self)
		base.Plane.__init__(self, space, normal, dist)

		self._inner_object = ode.GeomPlane(
			space.inner_object, normal, dist)


class NearCallbackArgs(base.NearCallbackArgs):
	pass
