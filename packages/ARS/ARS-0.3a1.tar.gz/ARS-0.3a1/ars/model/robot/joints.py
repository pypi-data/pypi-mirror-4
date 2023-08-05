from abc import ABCMeta, abstractmethod

import ode

import ars.exceptions as exc

class Joint:
	"""Abstract class. Not coupled (at all) with ODE or any other collision
	library/engine.

	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, world, inner_joint, body1=None, body2=None):
		self._world = world
		self._inner_joint = inner_joint
		self._body1 = body1
		self._body2 = body2

	@property
	def body1(self):
		return self._body1

	@property
	def body2(self):
		return self._body2

class Fixed(Joint):
	def __init__(self, world, body1, body2):
		try:
			inner_joint = ode.FixedJoint(world)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setFixed()

			super(Fixed, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type='Fixed joint')


class Rotary(Joint):
	def __init__(self, world, body1, body2, anchor, axis):

		try:
			inner_joint = ode.HingeJoint(world)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setAnchor(anchor)
			# TODO: see contrib.Ragdoll.addHingeJoint for possible modification
			inner_joint.setAxis(axis)

			# TODO: necessary?
			lo_stop = -ode.Infinity
			hi_stop = ode.Infinity
			inner_joint.setParam(ode.ParamLoStop, lo_stop)
			inner_joint.setParam(ode.ParamHiStop, hi_stop)

			super(Rotary, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type='Rotary joint')

	def add_torque(self, torque):
		"""Applies the torque about the rotation axis
		torque: float
		"""
		try:
			self._inner_joint.addTorque(torque)
		except:
			raise exc.JointError(self, 'Failed to add torque to this joint')

	@property
	def angle(self):
		"""Returns the angle (float) between the two bodies. Its value is
		between -pi and +pi. The zero angle is determined by the position of
		the bodies when joint anchor is set."""
		try:
			return self._inner_joint.getAngle()
		except:
			raise exc.JointError(self, 'Failed to get the angle of this joint')

	@property
	def angle_rate(self):
		"""Returns the angle rate (float)"""
		try:
			return self._inner_joint.getAngleRate()
		except:
			raise exc.JointError(self, 'Failed to get the angle rate of this joint')

	def set_speed(self, speed, max_force=None):
		if max_force:
			self._inner_joint.setParam(ode.ParamFMax, max_force)
		self._inner_joint.setParam(ode.ParamVel, speed)


class Universal(Joint):
	def __init__(self, world, body1, body2, anchor, axis1, axis2):

		try:
			inner_joint = ode.UniversalJoint(world)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setAnchor(anchor)
			# TODO: see contrib.Ragdoll.addHingeJoint for possible modification
			inner_joint.setAxis1(axis1)
			inner_joint.setAxis2(axis2)

			# TODO: necessary?
			lo_stop1 = -ode.Infinity
			hi_stop1 = ode.Infinity
			lo_stop2 = -ode.Infinity
			hi_stop2 = ode.Infinity
			inner_joint.setParam(ode.ParamLoStop, lo_stop1)
			inner_joint.setParam(ode.ParamHiStop, hi_stop1)
			inner_joint.setParam(ode.ParamLoStop2, lo_stop2)
			inner_joint.setParam(ode.ParamHiStop2, hi_stop2)

			super(Universal, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type='Universal joint')


class BallSocket(Joint):
	def __init__(self, world, body1, body2, anchor):

		try:
			inner_joint = ode.BallJoint(world)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setAnchor(anchor)

			super(BallSocket, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type='Ball and Socket joint')


class JointFeedback:
	def __init__(self, body1, body2, force1=None, force2=None, torque1=None,
			torque2=None):
		self._body1 = body1
		self._body2 = body2
		self.force1 = force1
		self.force2 = force2
		self.torque1 = torque1
		self.torque2 = torque2

	def get_body1(self):
		return self._body1

	@property
	def body2(self):
		return self._body2
