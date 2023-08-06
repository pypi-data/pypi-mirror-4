"""Shows usage of the JointTorque sensor, with the CentrifugalForce program.
Sensor data is stored in a queue, which is retrieved after the simulation ends
(but it can be accessed at any time).

Sensor is created in :meth:`create_sim_objects`.
>>> self.sensor = sensors.JointTorque(joint_object, self.sim)

It is updated automatically every time torque is added to the joint, i.e.
each time ``joint.addTorque(x)`` is called.

Sensor measurements can be easily retrieved at any time
>>> self.sensor.data_queue.pull()

"""
from ars.model.robot import sensors

from .base import CentrifugalForce, PrintDataMixin


class JointTorque(CentrifugalForce, PrintDataMixin):

	def create_sim_objects(self):
		CentrifugalForce.create_sim_objects(self)
		joint_object = self.sim.get_joint('r2')
		self.sensor = sensors.JointTorque(joint_object, self.sim)
