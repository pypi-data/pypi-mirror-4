
# Created on 2011.08.09
#
# @author: german

from abc import ABCMeta, abstractmethod

TIMER_PERIOD = 50 # milliseconds
TIMER_EVENT = 'TimerEvent'
KEY_PRESS_EVENT = 'KeyPressEvent'

class Axes:
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, position=(0,0,0), cylinder_radius=0.05):
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
	def __init__(self, center, rotation):
		self._position = center
		self._rotation = rotation
		self._color = None
		self._actor = None

	def update_position_rotation(self, position, rotation):
		self._position = position
		self._rotation = rotation
		self.adapter._update_body(self._actor, position, rotation)

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
	def __init__(self, size, position, rotation=None):
		super(Box, self).__init__(position, rotation)

class Cone(Body):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, height, radius, center, rotation=None, resolution = 100):
		super(Cone, self).__init__(center, rotation)

class Sphere(Body):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, radius, center, rotation=None, phiResolution = 50, thetaResolution = 50):
		super(Sphere, self).__init__(center, rotation)

class Cylinder(Body):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, length, radius, center, rotation=None, resolution=10):
		super(Cylinder, self).__init__(center, rotation)

class Capsule(Body):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, length, radius, center, rotation=None, resolution=10):
		super(Capsule, self).__init__(center, rotation)

class Trimesh(Body):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, vertices, faces, position=None, rotation=None):
		super(Trimesh, self).__init__(position, rotation)

class Adapter:
	"""
	Abstract class. Not coupled (at all) with VTK or any other graphics library
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		self.timer_count = 0
		self.on_idle_parent_callback = None
		self.on_reset_parent_callback = None
		self.on_key_press_parent_callback = None
		self._window_started = False

	@abstractmethod
	def create_window(self, title, position, size, zoom, cam_position, color):
		raise NotImplementedError()

	@abstractmethod
	def add_object(self, object_):
		raise NotImplementedError()

	def add_objects_list(self, objects_list_):
		for object_ in objects_list_:
			self.add_object(object_)

	@abstractmethod
	def start_window(self, on_idle_callback, on_reset_callback, on_key_press_callback):
		raise NotImplementedError()

	@abstractmethod
	def restart_window(self):
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
	def _update_body(body, position, rotation):
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
