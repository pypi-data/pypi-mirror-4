"""Base program classes to create demos using sensors.

"""
from ars.app import Program
import ars.constants as cts
from ars.lib.pydispatch import dispatcher
from ars.model.simulator import signals
import ars.utils.mathematical as mut


class PrintDataMixin:

	def print_final_data(self):
		collected_data = self.sensor.data_queue
		print('sensor data queue count %d' % collected_data.count())
		print(collected_data)


class CentrifugalForce(Program):

	"""Demo of a system where inertia and centrifugal force intervene."""

	OFFSET = (2, 0.5, 2)

	# ((size, center), density)
	BOX_PARAMS = (((5, 0.5, 5), (0, -0.25, 0)), {'density': 1})

	WINDOW_SIZE = (900, 600)
	CAMERA_POSITION = (2, 5, 10)  # position [meters]
	FPS = 50
	STEPS_PER_FRAME = 20  # 200 # STEP_SIZE = 1e-5 # 0.01 ms

	POLE_SPEED_STEP = 0.01
	POLE_VISUAL_RADIUS = 0.05  # 5 cm. how it will be displayed
	POLE_HEIGHT = 2  # 2 m
	POLE_INITIAL_POS = (0.0, 1.0, 0.0)  # (0.0,0.0,1.0) in C++ example

	BALL_MASS = 1.0  # 1kg
	BALL_RADIUS = 0.01  # 1 cm
	BALL_VISUAL_RADIUS = 0.1  # 10 cm
	BALL_INITIAL_POS = (0.0, 1.0, 1.0)

	JOINT1_ANCHOR = (0.0, 0.0, 0.0)
	JOINT1_AXIS = (0.0, 1.0, 0.0)  # (0.0,0.0,1.0) Z-axis in C++ example
	JOINT1_FMAX = 100
	JOINT2_ANCHOR = (
	0.0, 2.0, 1.0)  # (0.0,2.0,1.0) # (0.0,1.0,2.0) in C++ example
	JOINT2_AXIS = (1.0, 0.0, 0.0)  # X-axis

	CABLE_LENGTH = mut.length3(mut.sub3(BALL_INITIAL_POS, JOINT2_ANCHOR))

	JOINT2_ANGLE_RATE_CONTROLLER_KP = 500.0
	JOINT1_ANGLE_RATE_INITIAL = 3.0

	def __init__(self):
		Program.__init__(self)
		self.key_press_functions.add('a', self.inc_joint1_vel)
		self.key_press_functions.add('z', self.dec_joint1_vel)

		dispatcher.connect(self.on_pre_frame, signals.SIM_PRE_FRAME)

		self.joint1_vel_user = self.JOINT1_ANGLE_RATE_INITIAL
		self.large_speed_steps = True

	def create_sim_objects(self):
		"""Implementation of the required method.

		Creates and sets up all the objects of the simulation.

		"""
		box = self.sim.add_box(*self.BOX_PARAMS[0], **self.BOX_PARAMS[1])
		# Q: Shouldn't pole have mass?
		# A: Does not really matter because speed is set and fixed.
		pole = self.sim.add_cylinder(
			self.POLE_HEIGHT, self.POLE_VISUAL_RADIUS,
			self.POLE_INITIAL_POS, density=1.0)
		ball = self.sim.add_sphere(
			self.BALL_RADIUS, self.BALL_INITIAL_POS, mass=self.BALL_MASS)

		# bodies are rotated before attaching themselves through joints
		self.sim.get_object(pole).rotate(cts.X_AXIS, mut.pi / 2)

		self.sim.get_object(box).offset_by_position(self.OFFSET)
		self.sim.get_object(pole).offset_by_position(self.OFFSET)
		self.sim.get_object(ball).offset_by_position(self.OFFSET)

		self.joint1 = self.sim.add_rotary_joint(
			'r1',                        # name
			self.sim.get_object(box),    # obj1
			self.sim.get_object(pole),   # obj2
			None,                        # anchor
			self.JOINT1_AXIS)            # axis

		self.sim.add_rotary_joint(
			'r2',
			self.sim.get_object(pole),
			self.sim.get_object(ball),
			mut.add3(self.OFFSET, self.JOINT2_ANCHOR),
			self.JOINT2_AXIS)

		self.box = box
		self.pole = pole
		self.ball = ball

	def on_pre_frame(self):
		"""Handle simulation's pre-frame signal."""
		try:
			self.set_joint1_speed()
			self.apply_friction()
		except Exception as e:
			print('Exception when executing on_pre_frame: %s' % str(e))

	def inc_joint1_vel(self):
		"""Increase joint1's speed set point."""
		self.joint1_vel_user += self.POLE_SPEED_STEP

	def dec_joint1_vel(self):
		"""Decrease joint1's speed set point."""
		self.joint1_vel_user -= self.POLE_SPEED_STEP

	def set_joint1_speed(self):
		"""Set joint1's speed."""
		joint = self.sim.get_joint('r1').joint
		joint.set_speed(self.joint1_vel_user, self.JOINT1_FMAX)

	def apply_friction(self):
		"""Calculate friction torque and apply it to joint 'r2'."""
		kp = self.JOINT2_ANGLE_RATE_CONTROLLER_KP
		joint = self.sim.get_joint('r2').joint
		joint.add_torque(-kp * joint.angle_rate)


class CentrifugalForce2(CentrifugalForce):

	"""Small modification of :class:`CentrifugalForce`.

	Adds :meth:`on_post_step` handler to simulation's post-step signal.

	"""

	def __init__(self):
		CentrifugalForce.__init__(self)
		dispatcher.connect(self.on_post_step, signals.SIM_POST_STEP)

	def on_post_step(self):
		"""Handle simulation's post-step signal."""
		pass


class FallingBalls(Program):

	"""A very simple simulation: three falling balls impact the floor."""

	#==========================================================================
	# constants
	#==========================================================================
	BALL_CENTER = (0, 3, 5)
	BALL_RADIUS = 1.0
	BALL_MASS = 1.0
	BALL2_OFFSET = (0.5, 1, 2)

	STEPS_PER_FRAME = 100

	def create_sim_objects(self):
		"""Implementation of the required method.

		Creates and sets up all the objects of the simulation.

		"""
		self.ball1 = self.sim.add_sphere(
			self.BALL_RADIUS,
			self.BALL_CENTER,
			mass=self.BALL_MASS)
		self.ball2 = self.sim.add_sphere(
			self.BALL_RADIUS,
			mut.add3(self.BALL_CENTER, self.BALL2_OFFSET),
			mass=self.BALL_MASS)
