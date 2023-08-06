"""Module of all the classes related to sensors.

There are base classes for sensors whose source is a body, joint or simulation.
It also considers those which read information automatically by subscribing
to certain signals.

Some abstract classes are:

* :class:`Sensor`
* :class:`SingleSignalSensor`, :class:`MultipleSignalsSensor`
* :class:`BodySensor`
* :class:`JointSensor`
* :class:`SimulationSensor`


Some practical sensors are:

* :class:`RotaryJointSensor`, :class:`JointTorque`
* :class:`Laser`
* :class:`GPS`, :class:`Velometer`, :class:`Accelerometer`,
  :class:`Inclinometer`
* :class:`KineticEnergy`, :class:`PotentialEnergy`, :class:`TotalEnergy`,
  :class:`SystemTotalEnergy`

It also contains the auxiliary classes :class:`SensorData` and
:class:`SensorDataQueue`.

"""
from abc import ABCMeta, abstractmethod

from ...lib.pydispatch import dispatcher
from ...model.collision import adapters as coll
from ...utils import containers
from ...utils.generic import get_current_epoch_time
from ...utils.geometry import calc_inclination
from ...utils.mathematical import calc_acceleration

from . import signals

#==============================================================================
# Abstract classes
#==============================================================================


class Sensor:

	"""Abstract base class for all sensors.

	Sensor data is stored in a queue (:attr:`data_queue`), and it is
	usually retrieved after the simulation ends but can be accessed at any
	time::

	  measurement = sensor.data_queue.pull()

	.. warning::
	  Beware that :meth:`ars.utils.containers.Queue.pull` returns the first
	  element of the queue and **removes** it.

	"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, source):
		self._source = source
		self.data_queue = SensorDataQueue()

	def on_change(self, time=None):
		"""Build a :class:`SensorData` object and stores it in the
		:attr:`data_queue`.

		:param time: if None, current (computer's) time is used
		:type time: number or None

		"""
		dispatcher.send(signals.SENSOR_PRE_ON_CHANGE, sender=self, time=time)
		if time is None:
			time = get_current_epoch_time()

		data = self._build_data()
		data.set_time(time)
		self.data_queue.put(data)
		dispatcher.send(signals.SENSOR_POST_ON_CHANGE, sender=self, data=data)

	@abstractmethod
	def _build_data(self):
		"""Create and return a :class:`SensorData` object."""
		raise NotImplementedError()

	def get_measurement(self):
		"""Return a measurement of the sensor packed in a data structure."""
		return self._build_data()

	@property
	def source(self):
		return self._source


class BaseSignalSensor:

	"""Base class for sensors that handle signals with :meth:`on_send`."""

	__metaclass__ = ABCMeta

	any_sender = dispatcher.Any

	@abstractmethod
	def __init__(self, sender=any_sender, autotime=False):
		"""Constructor.

		:param sender: object that will send the signal; if it is
			:attr:`any_sender`, subscription will be to any object
		:param autotime: if True and :meth:`_get_time` is not overriden, every
			measurement's time will set to the computer time in that instant

		"""
		self._sender = sender
		self._autotime = autotime

		self.data_queue = SensorDataQueue()

	def on_send(self, sender, *args, **kwargs):
		"""Handle signal sent/fired by ``sender`` through the dispatcher.

		Takes care of building a data object, set time to it and save it in the
		``data_queue``.

		:param sender: signal sender
		:param args: signal arguments
		:param kwargs: signal keyword arguments

		"""
		data = self._build_data(sender, *args, **kwargs)
		time = self._get_time()
		if time is not None:
			data.set_time(time)
		self.data_queue.put(data)

	@abstractmethod
	def _build_data(self, sender, *args, **kwargs):
		"""Build and return a SensorData object with current data.

		:return: object containing data based on the state of the sender
		:rtype: :class:`SensorData`

		"""
		raise NotImplementedError()

	def _get_time(self):
		"""Return the time to set to the :class`SensorData` instance.

		Override this to define it based on some object's state or property.

		:return: time value for the data
		:rtype: :class:`float` or None

		"""
		time = None
		if self._autotime:
			time = get_current_epoch_time()
		return time

	@property
	def sender(self):
		"""Return the sender of the signal to which the sensor listens."""
		return self._sender


class SingleSignalSensor(BaseSignalSensor):

	"""Abstract base class for sensors subscribed to one signal."""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, signal, *args, **kwargs):
		"""Constructor.

		:param signal: signal to subscribe to

		"""
		super(SingleSignalSensor, self).__init__(*args, **kwargs)
		self._signal = signal

		# subscribe :meth:`on_send` handler to the signal sent by ``sender``
		dispatcher.connect(self.on_send, signal=self._signal,
			sender=self._sender)


class MultipleSignalsSensor(BaseSignalSensor):

	"""Abstract base class for sensors subscribed to multiple signals."""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, signals, *args, **kwargs):
		"""Constructor.

		:param signals: signals to subscribe to
		:type signals: iterable

		"""
		super(MultipleSignalsSensor, self).__init__(*args, **kwargs)
		self._signals = signals

		# subscribe :meth:`on_send` handler to the signals in :attr:`_signals`
		# sent by ``sender``
		for signal in self._signals:
			dispatcher.connect(self.on_send, signal=signal,
				sender=self._sender)


class BodySensor(Sensor):

	"""Abstract base class for sensors whose source of data is a body."""

	__metaclass__ = ABCMeta

	def __init__(self, body):
		super(BodySensor, self).__init__(body)

	@property
	def body(self):
		return self.source


class JointSensor(Sensor):

	"""Abstract base class for sensors whose source of data is a joint."""

	__metaclass__ = ABCMeta

	def __init__(self, joint):
		super(JointSensor, self).__init__(joint)

	@property
	def joint(self):
		return self.source


class ActuatedJointSensor(JointSensor):

	"""Sensor whose source of data is an ``ActuatedJoint`` joint."""

	__metaclass__ = ABCMeta


class SimulationSensor(Sensor):

	"""Abstract base class for sensors whose source of data is a simulation."""

	__metaclass__ = ABCMeta

	def __init__(self, sim):
		"""Constructor.

		:param sim: simulation
		:type sim: :class:`ars.model.simulator.Simulation`

		"""
		super(SimulationSensor, self).__init__(sim)

	@property
	def sim(self):
		"""Return the simulation object.

		:return: simulation
		:rtype: :class:`ars.model.simulator.Simulation`

		"""
		return self.source

#==============================================================================
# classes
#==============================================================================


class RotaryJointSensor(JointSensor):

	"""Sensor measuring the angle (and its rate) of a rotary joint."""

	def _build_data(self):
		kwargs = {
			'angle': self.joint.angle,
			'angle_rate': self.joint.angle_rate,
			}
		return SensorData(**kwargs)


class JointTorque(SingleSignalSensor):

	"""Sensor measuring torque added to a joint."""

	signal = signals.JOINT_POST_ADD_TORQUE

	def __init__(self, sim_joint, sim):
		# The sender to connect to is sim_joint.joint because
		# :class:`SimulatedJoint` wraps the "real" joint object that sends the
		# signal.
		super(JointTorque, self).__init__(signal=self.signal,
			sender=sim_joint.joint)
		self._sim = sim

	def _build_data(self, sender, *args, **kwargs):
		return SensorData(**{'torque': kwargs.get('torque')})

	def _get_time(self):
		return self._sim.sim_time


class JointForce(SingleSignalSensor):

	"""Sensor measuring force 'added' to a joint."""

	signal = signals.JOINT_POST_ADD_FORCE

	def __init__(self, sim_joint, sim):
		super(JointForce, self).__init__(signal=self.signal,
			sender=sim_joint.joint)
		self._sim = sim

	def _build_data(self, sender, *args, **kwargs):
		return SensorData(**{'force': kwargs.get('force')})

	def _get_time(self):
		return self._sim.sim_time


class JointPower(MultipleSignalsSensor):

	"""Sensor measuring power applied by a joint (due to force and torque)."""

	signals = [JointTorque.signal, JointForce.signal]
	
	def __init__(self, sim_joint, sim):
		super(JointPower, self).__init__(signals=self.signals,
			sender=sim_joint.joint)
		self._sim = sim

	def _build_data(self, sender, *args, **kwargs):
		power = 0.0
		# both are scalars (float)
		torque = kwargs.get('torque')
		force = kwargs.get('force')

		try:
			if torque is not None:
				power += torque * sender.angle_rate
			if force is not None:
				power += force * sender.position_rate
		except Exception as e:
			print('Error when calculating power. Exception:\n%s' % e)

		return SensorData(**{'power': power})
	
	def _get_time(self):
		return self._sim.sim_time


class Laser(Sensor):

	"""Laser scanner."""

	def __init__(self, space, max_distance=10.0):
		self._ray = coll.Ray(space, max_distance)
		super(Laser, self).__init__(self._ray)

	def on_change(self, time=get_current_epoch_time()):
		super(Laser, self).on_change(time)
		self._ray.clear_contacts()

	def set_position(self, pos):
		"""Set position of the ray.

		Useful mainly when it is not attached to a body.

		:param pos: position
		:type pos: 3-sequence of floats

		"""
		# TODO: if mounted, w.r.t what?
		self._ray.set_position(pos)

	def set_rotation(self, rot):
		"""Set rotation of the ray.

		Useful mainly when it is not attached to a body.

		:param rot: rotation matrix
		:type rot: 9-sequence of floats

		"""
		# TODO: if mounted, w.r.t what?
		self._ray.set_rotation(rot)

	def get_ray(self):
		return self._ray

	def _build_data(self):
		ray_contact = self._ray.get_closer_contact()
		if ray_contact is None:
			kwargs = {'distance': None}
		else:
			kwargs = {'distance': ray_contact.depth}
		return SensorData(**kwargs)


class LaserRangeFinder(BodySensor):

	"""Laser range finder."""

	pass


class GPS(BodySensor):

	"""Retrieve a body's XYZ position."""

	def _build_data(self):
		kwargs = {'position': self.body.get_position()}
		return SensorData(**kwargs)


class Velometer(BodySensor):

	"""Calculate and retrieve a body's linear and angular velocity."""

	def _build_data(self):
		kwargs = {'linear velocity': self.body.get_linear_velocity(),
					'angular velocity': self.body.get_angular_velocity(), }
		return SensorData(**kwargs)


class Accelerometer(BodySensor):

	"""Calculate and retrieve a body's linear and angular acceleration.

	.. warning::
	  The provided `time_step` is used to calculate the acceleration based on
	  the velocity measured at two instants in time. If subsequent calls to
	  `on_change` are separated by a simulation time period different to the
	  given `time_step`, the results will be invalid.

	"""

	def __init__(self, body, time_step):
		super(Accelerometer, self).__init__(body)
		self._time_step = time_step

	def _build_data(self):
		linear_vel_prev, angular_vel_prev = self.body.get_saved_velocities()

		linear_vel = self.body.get_linear_velocity()
		angular_vel = self.body.get_angular_velocity()
		self.body.save_velocities()

		linear_accel = calc_acceleration(self._time_step,
			linear_vel_prev, linear_vel)
		angular_accel = calc_acceleration(self._time_step,
			angular_vel_prev, angular_vel)

		kwargs = {'linear acceleration': linear_accel,
				  'angular acceleration': angular_accel, }
		return SensorData(**kwargs)


class Inclinometer(BodySensor):

	"""Retrieve a body's `pitch` and `roll`."""

	def _build_data(self):
		pitch, roll = calc_inclination(self.body.get_rotation())
		kwargs = {'pitch': pitch, 'roll': roll}
		return SensorData(**kwargs)


class KineticEnergy(BodySensor):

	r"""Retrieve a body's kinetic energy, both due to translation and rotation.

	.. math::
		E_t &= \frac{1}{2} m v^2 = \frac{1}{2} m \cdot v^\top v \\
		E_r &= \frac{1}{2} I \omega^2 = \frac{1}{2} \omega^\top \mathbf{I} \omega

	"""

	def _build_data(self):
		kwargs = {
			'translation energy': self.body.calc_translation_kinetic_energy(),
			'rotation energy': self.body.calc_rotation_kinetic_energy(), }
		return SensorData(**kwargs)


class PotentialEnergy(BodySensor):

	r"""Retrieve a body's potential energy.

	Calculated based on the current position (`x`) and world's gravitational
	acceleration (`g`).

	.. math::
		E_p = m \cdot g \cdot h = - m \cdot g^\top x

	"""

	def __init__(self, body, gravity):
		super(PotentialEnergy, self).__init__(body)
		self._gravity = gravity

	def _build_data(self):
		potential_e = self.body.calc_potential_energy(self._gravity)
		kwargs = {'potential energy': potential_e, }
		return SensorData(**kwargs)


class TotalEnergy(BodySensor):

	r"""Retrieve a body's potential and kinetic energy.

	The kinetic energy accounts for translation and rotation.

	.. math::
		E_p &= m \cdot g \cdot h = - m \cdot g^\top x \\
		E_k &= \frac{1}{2} m \cdot v^\top v
		  + \frac{1}{2} \omega^\top \mathbf{I} \omega

	"""

	def __init__(self, body, gravity, disaggregate=False):
		super(TotalEnergy, self).__init__(body)
		self._gravity = gravity
		self._disaggregate = disaggregate

	def _build_data(self):
		potential_e = self.body.calc_potential_energy(self._gravity)
		linear_ke = self.body.calc_translation_kinetic_energy()
		angular_ke = self.body.calc_rotation_kinetic_energy()

		if self._disaggregate:
			kwargs = {
				'potential energy': potential_e,
				'kinetic energy': linear_ke + angular_ke, }
		else:
			kwargs = {'total energy': potential_e + linear_ke + angular_ke, }
		return SensorData(**kwargs)


class SystemTotalEnergy(SimulationSensor):

	r"""Retrieve a system's total potential and kinetic energy.

	It considers all bodies in the simulation. The kinetic energy accounts for
	translation and rotation.

	.. math::
		E_p &= m \cdot g \cdot h = - m \cdot g^\top x \\
		E_k &= \frac{1}{2} m \cdot v^\top v
		  + \frac{1}{2} \omega^\top \mathbf{I} \omega

	"""

	def __init__(self, sim, disaggregate=False):
		super(SystemTotalEnergy, self).__init__(sim)
		self._disaggregate = disaggregate

	def _build_data(self):
		gravity = self.sim.gravity
		bodies = self.sim.get_bodies()
		potential_e = 0.0
		linear_ke = 0.0
		angular_ke = 0.0

		for body in bodies:
			potential_e += body.calc_potential_energy(gravity)
			linear_ke += body.calc_translation_kinetic_energy()
			angular_ke += body.calc_rotation_kinetic_energy()

		if self._disaggregate:
			kwargs = {
				'potential energy': potential_e,
				'kinetic energy': linear_ke + angular_ke, }
		else:
			kwargs = {'total energy': potential_e + linear_ke + angular_ke, }
		return SensorData(**kwargs)

#==============================================================================
# aux classes
#==============================================================================


class SensorData:

	"""Data structure to pack a sensor measurement's information."""

	def __init__(self, *args, **kwargs):
		self._time = None
		self._args = args		# as a tuple?
		self._kwargs = kwargs 	# as a dictionary?

	def get_time(self):
		return self._time

	def set_time(self, time):
		self._time = time

	def get_args(self):
		return self._args

	def get_kwargs(self):
		return self._kwargs

	def get_arg(self, index):
		return self._args[index]

	def get_kwarg(self, key):
		return self._kwargs[key]

	def __str__(self):
		line = '|'
		if self._time is not None:
			line = ' %f |' % self._time
		for arg in self._args:
			line += ' %s |' % str(arg)
		for key in self._kwargs:
			line += ' %s: %s |' % (str(key), str(self._kwargs[key]))
		return line


class SensorDataQueue(containers.Queue):

	"""Queue-like container for sensor measurements."""

	pass
