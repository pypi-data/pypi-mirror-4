from abc import ABCMeta, abstractmethod

TIMER_PERIOD = 50  # milliseconds
TIMER_EVENT = 'TimerEvent'
KEY_PRESS_EVENT = 'KeyPressEvent'


class Axes:

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, pos=(0, 0, 0), rot=None, cylinder_radius=0.05):
		self._actor = None

	@property
	def actor(self):
		return self._actor


class Body:

	"""
	Abstract class. Not coupled (at all) with VTK or any other graphics library

	"""

	__metaclass__ = ABCMeta

	adapter = None

	@abstractmethod
	def __init__(self, center, rot):
		self._position = center
		self._rotation = rot
		self._color = None
		self._actor = None

	def update_position_rotation(self, pos, rot):
		self._position = pos
		self._rotation = rot
		self.adapter._update_pose(self._actor, pos, rot)

	@property
	def actor(self):
		return self._actor

	@abstractmethod
	def get_color(self):
		return self._color

	@abstractmethod
	def set_color(self, color):
		self._color = color


class Box(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, size, pos, rot=None):
		super(Box, self).__init__(pos, rot)


class Cone(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, height, radius, center, rot=None, resolution=100):
		"""Constructor.

		:param resolution: it is the circumferential number of facets
		:type resolution: int

		"""
		super(Cone, self).__init__(center, rot)


class Sphere(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, radius, center, rot=None, phi_resolution=50,
                 theta_resolution=50):
		"""Constructor.

		:param phi_resolution: resolution in the latitude (phi) direction
		:type phi_resolution: int
		:param theta_resolution: resolution in the longitude (theta) direction
		:type theta_resolution: int

		"""
		super(Sphere, self).__init__(center, rot)


class Cylinder(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, length, radius, center, rot=None, resolution=10):
		super(Cylinder, self).__init__(center, rot)


class Capsule(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, length, radius, center, rot=None, resolution=10):
		super(Capsule, self).__init__(center, rot)


class Trimesh(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, vertices, faces, pos=None, rot=None):
		super(Trimesh, self).__init__(pos, rot)


class Adapter:

	"""
	Abstract class. Not coupled (at all) with VTK or any other graphics library

	"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, *args, **kwargs):
		self.timer_count = 0
		self.on_idle_parent_callback = None
		self.on_reset_parent_callback = None
		self.on_key_press_parent_callback = None
		self._window_started = False

	@abstractmethod
	def add_object(self, object_):
		raise NotImplementedError()

	def add_objects_list(self, objects_list_):
		for object_ in objects_list_:
			self.add_object(object_)

	@abstractmethod
	def start_window(
            self, on_idle_callback, on_reset_callback, on_key_press_callback):
		raise NotImplementedError()

	@abstractmethod
	def restart_window(self):
		raise NotImplementedError()

	@abstractmethod
	def finalize_window(self):
		"""Finalize window and remove/clear associated resources."""
		raise NotImplementedError()

	@abstractmethod
	def _timer_callback(self, obj, event):
		raise NotImplementedError()

	@abstractmethod
	def _key_press_callback(self, obj, event):
		raise NotImplementedError()

	@abstractmethod
	def reset(self):
		raise NotImplementedError()

	@staticmethod
	@abstractmethod
	def _update_pose(obj, pos, rot):
		raise NotImplementedError()


class ScreenshotRecorder:

	__metaclass__ = ABCMeta

	def __init__(self, base_filename):
		self.base_filename = base_filename
		self.last_write_time = None
		self.period = None

	@abstractmethod
	def write(self, index, time):
		"""
		Writes the current image displayed in the render window as a file
		named 'self.base_filename' with	the 'index' number appended, and the
		corresponding extension.

		"""
		raise NotImplementedError()
