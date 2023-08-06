"""Shows usage of the JointPower sensor, with the CentrifugalForce program.
Sensor data is stored in a queue, which is retrieved after the simulation ends
(but it can be accessed at any time).

Sensor is created in :meth:`create_sim_objects`.
>>> self.sensor = sensors.JointPower(joint_object, self.sim)

It is updated automatically every time torque or force is added to the joint,
i.e. each call to ``joint.add_torque`` or ``joint.add_force``.

Sensor measurements can be easily retrieved at any time
>>> self.sensor.data_queue.pull()

"""
from ars.model.robot import sensors

from .base import CentrifugalForce, PrintDataMixin


class JointPower(CentrifugalForce, PrintDataMixin):

	"""Simulation of a virtual power sensor attached to a joint (``r2``).

	This joint is not powered but because friction is considered
	an external	torque is applied at each simulation step
	(see :meth:`apply_friction`). Because it is a friction torque,
	the applied power is negative.

	The laser is positioned at :attr:`RAY_POS` and its detection range
	is determined by :attr:`RAY_LENGTH`. The default orientation
	(positive Z-axis) of the :class:`ars.model.robot.sensors.Laser`
	may be modified with :attr:`RAY_ROTATION`.

	.. seealso::
		:class:`ars.model.robot.sensors.Sensor`

	The sensor is created in :meth:`create_sim_objects`:
		`self.sensor = sen.Laser(space, self.RAY_LENGTH)`
		`self.sensor.set_position(self.RAY_POS)`

	and it is updated in :meth:`on_post_step`:
		`self.sensor.on_change(time)`

	"""

	def create_sim_objects(self):
		CentrifugalForce.create_sim_objects(self)
		joint_object = self.sim.get_joint('r2')
		self.sensor = sensors.JointPower(joint_object, self.sim)
