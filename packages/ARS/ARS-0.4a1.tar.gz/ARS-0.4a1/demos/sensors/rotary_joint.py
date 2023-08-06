"""Use of the RotaryJointSensor with CentrifugalForceTest program.
Sensor data is stored in a queue, which is retrieved after the simulation ends
(but it can be accessed at any time).

Sensor is created in the `create_sim_objects` method.
	'self.sensor = sensors.RotaryJointSensor(self.sim.get_joint('r2').joint)'
It is updated in the `on_pre_frame` method
	'self.sensor.on_change(time)'
Sensor measurements can be retrieved at any time
	'self.sensor.data_queue.pull()'

"""
from ars.model.robot import sensors

from .base import CentrifugalForce, PrintDataMixin


class RotaryJointSensor(CentrifugalForce, PrintDataMixin):

	def create_sim_objects(self):
		CentrifugalForce.create_sim_objects(self)
		self.sensor = sensors.RotaryJointSensor(
			self.sim.get_joint('r2').joint)

	def on_pre_frame(self):
		# superclass' `on_pre_frame` sets r1 speed and applies friction to r2
		super(RotaryJointSensor, self).on_pre_frame()
		try:
			time = self.sim.sim_time
			self.sensor.on_change(time)
		except Exception as e:
			print('Exception when executing on_pre_frame: %s' % str(e))
