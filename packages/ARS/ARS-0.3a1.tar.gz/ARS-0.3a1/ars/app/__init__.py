"""Main package of the software.
It contains the Program class which is the core application controller.

"""

from abc import abstractmethod

import ars.exceptions as exc
import ars.graphics.adapters as gp
from ars.lib.pydispatch import dispatcher
from ars.model.simulator import Simulation, SIM_PRE_FRAME_SIGNAL

class Program():
	"""Main class of ARS.

	To run a custom simulation, create a subclass.
	It must contain an implementation of the 'create_sim_objects' method
	which will be called during the simulation creation.

	To use it, only two statements are necessary:
	-create an object of this class (i.e. sim_program = ProgramSubclass() )
	-call its 'start' method (i.e. sim_program.start() )

	"""

	DEBUG = False
	PRINT_KEY_INFO = True

	WINDOW_TITLE = "Autonomous Robot Simulator"
	WINDOW_POSITION = (0, 0)
	WINDOW_SIZE = (1024, 768)  # (width,height)
	WINDOW_ZOOM = 1.0
	CAMERA_POSITION = (10, 8, 10)

	BACKGROUND_COLOR = (1, 1, 1)

	FPS = 50
	STEPS_PER_FRAME = 50

	FLOOR_BOX_SIZE = (10, 0.01, 10)

	def __init__(self):
		"""Constructor. Defines some attributes and calls some initialization
		methods to:
		-sets the basic mapping of key to action,
		-create the visualization window according to class constants,
		-create the simulation.

		"""
		self.do_create_window = True

		self.key_press_functions = None
		self.sim = None
		self._screenshot_recorder = None

		# (key -> action) mapping
		self.set_key_2_action_mapping()

		self.gAdapter = gp.VtkAdapter()
		self.gAdapter.create_window(self.WINDOW_TITLE,
			self.WINDOW_POSITION,
			self.WINDOW_SIZE,
			zoom=self.WINDOW_ZOOM,
			background_color=self.BACKGROUND_COLOR,
			cam_position=self.CAMERA_POSITION)

		self.create_simulation()

	def start(self):
		"""Starts (indirectly) the simulation handled by this class by starting
		the visualization window. If it is closed, the simulation ends. It will
		restart if :attr:`do_create_window` has been previously set to ``True``.

		"""
		while self.do_create_window:
			self.do_create_window = False
			self.gAdapter.start_window(self.sim.on_idle, self.reset_simulation,
				self.on_action_selection)

	def reset_simulation(self):
		"""Resets the simulation by resetting the graphics adapter and creating
		a new simulation.

		"""
		if self.PRINT_KEY_INFO:
			print("reset simulation")
		self.do_create_window = True
		self.gAdapter.reset()
		self.create_simulation()

	def create_simulation(self, add_axes=True, add_floor=True):
		"""Creates an empty simulation and:
		-adds basic simulation objects (:meth:`add_basic_simulation_objects`),
		-(if ``add_axes`` is ``True``) adds axes to the visualization at the
		coordinates-system origin,
		-(if ``add_floor`` is ``True``) adds a floor with a defined normal
		vector and some visualization parameters,
		-calls :meth:`create_sim_objects` (which must be implemented by
		subclasses),
		-gets the actors representing the simulation objects and adds them to
		the graphics adapter.

		"""
		# set up the simulation parameters
		self.sim = Simulation(self.FPS, self.STEPS_PER_FRAME)
		self.sim.add_basic_simulation_objects()

		if add_axes:
			self.sim.add_axes()
		if add_floor:
			self.sim.add_floor(normal=(0, 1, 0), box_size=self.FLOOR_BOX_SIZE,
				color=(0.7, 0.7, 0.7))

		self.create_sim_objects()

		# add the graphic objects
		self.gAdapter.add_objects_list(self.sim.actors.values())
		self.sim.update_actors()

	@abstractmethod
	def create_sim_objects(self):
		"""This method must be overriden (at least once in the inheritance tree)
		by the subclass that will instatiated to run the simulator.
		It shall contain statements calling its 'sim' attribute's methods for
		adding objects (e.g. add_sphere). For example:
		self.sim.add_sphere(0.5, (1,10,1), density=1)

		"""
		raise NotImplementedError()

	def set_key_2_action_mapping(self):
		"""Creates an Action map, assigns it to :attr:`key_press_functions`
		and then adds some ``(key, function`` tuples.

		"""
		# TODO: add to constructor ``self.key_press_functions = None``?
		self.key_press_functions = ActionMap()
		self.key_press_functions.add('r', self.reset_simulation)

	def on_action_selection(self, key):
		"""Method called after an actions is selected by pressing a key."""
		if self.PRINT_KEY_INFO:
			print(key)
		try:
			if self.key_press_functions.has_key(key):
				if self.key_press_functions.is_repeat(key):
					f = self.key_press_functions.get_function(key)
					self.sim.all_frame_steps_callbacks.append(f)
				else:
					self.key_press_functions.call(key)
			else:
				if self.PRINT_KEY_INFO:
					print('unregistered key: %s' % key)
		except Exception as ex:
			print(ex)

	#==========================================================================
	# other
	#==========================================================================

	def on_pre_step(self):
		"""This method will be called before each integration step of the simulation.
		It is meant to be, optionally, implemented by subclasses.

		"""
		raise NotImplementedError()

	def on_pre_frame(self):
		"""This method will be called before each visualization frame is created.
		It is meant to be, optionally, implemented by subclasses.

		"""
		raise NotImplementedError()

	def create_screenshot_recorder(self, base_filename, periodically=False):
		"""Create a screenshot (of the frames displayed in the graphics window)
		recorder.
		
		Each image will be written to a numbered file according to
		``base_filename``. By default it will create an image each time
		:meth:`record_frame` is called. If ``periodically`` is ``True`` then
		screenshots will be saved in sequence. The time period between each
		frame is determined according to :attr:`FPS`.

		"""
		self._screenshot_recorder = gp.ScreenshotRecorder(base_filename,
			self.gAdapter)
		if periodically:
			period = 1.0 / self.FPS
			self._screenshot_recorder.period = period
		dispatcher.connect(self.record_frame, SIM_PRE_FRAME_SIGNAL)

	def record_frame(self):
		"""Record a frame using a screenshot recorder.
		
		If frames are meant to be written periodically, a new one will be
		recorded only if enough time has elapsed, otherwise it will return
		``False``. The filename index will be ``time / period``.
		
		If frames are not meant to be written periodically, then index equals
		simulator's frame number.

		"""
		if self._screenshot_recorder is None:
			raise exc.ArsError('Screenshot recorder is not initialized')

		try:
			time = self.sim.sim_time
			period = self._screenshot_recorder.period

			if period is None:
				self._screenshot_recorder.write(self.sim.num_frame)
			else:
				self._screenshot_recorder.write(self.sim.num_frame, time)
		except Exception:
			raise exc.ArsError('Could not record frame')


class ActionMap:
	def __init__(self):
		self._map = {}

	def add(self, key, value, repeat=False):
		self._map[key] = (value, repeat)

	def has_key(self, key):
		return self._map.has_key(key)

	def get(self, key, default=None):
		return self._map.get(key, default)

	def get_function(self, key):
		return self._map.get(key)[0]

	def call(self, key):
		try:
			self._map[key][0]()
		except Exception as ex:
			print(ex)

	def is_repeat(self, key):
		return self._map.get(key)[1]

	def __str__(self):
		raise NotImplementedError()
