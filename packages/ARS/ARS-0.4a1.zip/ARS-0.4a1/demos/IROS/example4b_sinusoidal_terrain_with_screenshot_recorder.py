"""Example #4 with a screenshot recorder.

"""
from .example4_sinusoidal_terrain import Example4


class Example4SR(Example4):

	# screenshot recorder
	RECORDER_BASE_FILENAME = 'sin'
	RECORD_PERIODICALLY = True

	def __init__(self):
		Example4.__init__(self)
		self.create_screenshot_recorder(
			self.RECORDER_BASE_FILENAME, self.RECORD_PERIODICALLY)
