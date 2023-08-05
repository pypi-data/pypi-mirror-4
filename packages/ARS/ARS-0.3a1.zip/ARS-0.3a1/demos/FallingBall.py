#!/usr/bin/env python

# Created on 2011.12.09
#
# @author: german

"""
Runs the simplest simulation ever: a falling ball impacts the floor
"""

from ars.app import Program

class FallingBall(Program):
	
	def create_sim_objects(self):
		self.sim.add_sphere(0.5, (1,10,1), density=1) # radius, center, density

if __name__ == '__main__':
	sim_program = FallingBall()
	sim_program.start()