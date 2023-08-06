from ars.graphics import adapters as graphics_adapter
from ars.lib.pydispatch import dispatcher
from ars.model.robot import sensors
from ars.model.simulator import signals
from ars.utils import geometry as gmt
from ars.utils import mathematical as mut

from .base import FallingBalls, PrintDataMixin


class LaserSensor(FallingBalls, PrintDataMixin):

	"""Simulation of a laser sensor detecting intersection with a ball as it
	falls.

	The laser is positioned at :attr:`RAY_POS` and its range equals
	:attr:`RAY_LENGTH`. The default orientation (positive Z-axis) of the
	the :class:`ars.model.robot.sensors.Laser` may be modified with
	:attr:`RAY_ROTATION`.

	.. seealso::
		:class:`ars.model.robot.sensors.Sensor`

	Sensor is created in the `create_sim_objects` method.
		`self.sensor = sensors.Laser(space, self.RAY_LENGTH)`
		`self.sensor.set_position(self.RAY_POS)`

	It is updated in the `on_post_step` method
		`self.sensor.on_change(time)`

	"""

	RAY_LENGTH = 1000.0
	RAY_POS = (0, 2, 0)

	BACKGROUND_COLOR = (0, 0, 0)

	# no rotation is the same as (any_axis, 0)
	RAY_ROTATION = gmt.calc_rotation_matrix((1, 0, 0), 0)
	#RAY_ROTATION = mut.calc_rotation_matrix((1, 0, 0), mut.pi / 4)
	#RAY_ROTATION = mut.calc_rotation_matrix((1, 0, 0), 7 * mut.pi / 16)

	def __init__(self):
		FallingBalls.__init__(self)
		dispatcher.connect(self.on_post_step, signals.SIM_POST_STEP)

	def create_simulation(self, *args, **kwargs):
		FallingBalls.create_simulation(self, add_axes=True, add_floor=False)

	def create_sim_objects(self):
		FallingBalls.create_sim_objects(self)
		space = self.sim.collision_space
		self.sensor = sensors.Laser(space, self.RAY_LENGTH)
		self.sensor.set_position(self.RAY_POS)
		#self.sensor.set_rotation(self.RAY_ROTATION)

	def on_post_step(self):
		try:
			time = self.sim.sim_time
			self.sensor.on_change(time)
		except Exception as e:
			print('Exception when executing on_post_step: %s' % str(e))


class VisualLaser(LaserSensor):

	"""A simulation identical to :class:`LaserSensor` but more
	interesting visually. For each intersection of the laser and an object,
	a small colored sphere is shown.

	.. warning::
		The viewer may need to rotate the scene to see these spheres. To do
		that, just click anywhere on the visualization, hold, and drag.

	"""

	SIGNAL = sensors.signals.SENSOR_POST_ON_CHANGE
	SPHERE_RADIUS = 0.05
	SPHERE_COLOR = (1.0, 1.0, 0.0)

	def __init__(self):
		super(VisualLaser, self).__init__()
		self.intersection_point = None
		dispatcher.connect(self.on_post_on_change, self.SIGNAL)

	def on_post_step(self):
		if self.intersection_point is not None:
			self.gAdapter.remove_object(self.intersection_point)
			self.intersection_point = None
		super(VisualLaser, self).on_post_step()

	def on_post_on_change(self, sender, *args, **kwargs):
		"""Create and paint laser's closest contact point.

		The sensor data is included in ``kwargs``. This method is to be
		called at the the end of :meth:`sensors.Sensor.on_change`, when
		the measurement has already been calculated.

		:param sender: signal sender
		:param args: signal data
		:param kwargs: signal data

		"""
		distance = kwargs.get('data').get_kwarg('distance')
		if distance is not None:
			position = self._calc_intersection(distance)
			self.intersection_point = graphics_adapter.Sphere(
				radius=self.SPHERE_RADIUS, center=position)
			self.intersection_point.set_color(self.SPHERE_COLOR)
			self.gAdapter.add_object(self.intersection_point)

	def _calc_intersection(self, distance):
		ray = self.sensor.get_ray()
		laser_pos = ray.get_position()
		laser_rot = ray.get_rotation()

		distance_vector = mut.mult_by_scalar3(mut.Z_AXIS, distance)
		offset = mut.rotate3(laser_rot, distance_vector)
		position = mut.add3(laser_pos, offset)
		return position
