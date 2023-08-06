"""Runs a simulation of a vehicle with two powered wheels and one
free-rotating spherical wheel.

"""
from .Vehicle2 import Vehicle2


class Vehicle2WithScreenshots(Vehicle2):
	FPS = 100 # this is the recording frequency
	RECORDER_BASE_FILENAME = 'test'
	RECORD_PERIODICALLY = True

	def __init__(self):
		Vehicle2.__init__(self)
		self.create_screenshot_recorder(
			self.RECORDER_BASE_FILENAME, self.RECORD_PERIODICALLY)
