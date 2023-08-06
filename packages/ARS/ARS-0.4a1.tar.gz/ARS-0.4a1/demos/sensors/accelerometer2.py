"""Shows usage of the Accelerometer sensor, with the CentrifugalForce2 program.
Sensor data is stored in a queue, which is retrieved after the simulation ends
(but it can be accessed at any time).

Sensor is created in the `create_sim_objects` method.
	'self.sensor = sensors.Accelerometer(ball_object, self.sim.time_step)'
It is updated in the `on_post_step` method
	'self.sensor.on_change(time)'
Sensor measurements can be retrieved at any time
	'self.sensor.data_queue.pull()'

"""
from ars.model.robot import sensors

from .base import CentrifugalForce2, PrintDataMixin


class Accelerometer(CentrifugalForce2, PrintDataMixin):

	def create_sim_objects(self):
		CentrifugalForce2.create_sim_objects(self)
		ball_object = self.sim.get_object(self.ball)
		self.sensor = sensors.Accelerometer(ball_object, self.sim.time_step)

	def on_post_step(self):
		try:
			time = self.sim.sim_time
			self.sensor.on_change(time)
		except Exception as e:
			print('Exception when executing on_post_step: %s' % str(e))
