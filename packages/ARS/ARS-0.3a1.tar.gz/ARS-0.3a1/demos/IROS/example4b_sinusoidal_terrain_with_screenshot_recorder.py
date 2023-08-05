#!/usr/bin/env python

# Created on 2012.01.16
#
# @author: german

"""
Example #4 with a screenshot recorder
"""

from example4_sinusoidal_terrain import Example4

class Example4SR(Example4):

	# screenshot recorder
	RECORDER_BASE_FILENAME = 'sin'
	RECORD_PERIODICALLY = True

	def __init__(self):
		"""Constructor, calls the superclass constructor first"""
		Example4.__init__(self)
		self.create_screenshot_recorder(
			self.RECORDER_BASE_FILENAME, self.RECORD_PERIODICALLY)

if __name__ == '__main__':
	sim_program = Example4SR()
	sim_program.start()