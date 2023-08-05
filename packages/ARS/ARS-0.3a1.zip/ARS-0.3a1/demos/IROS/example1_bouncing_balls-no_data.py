#!/usr/bin/env python

# Created on 2012.03.08
#
# @author: german

"""
Example #1, with 3 balls (different colors) and no data output
"""

from ars.app import Program

class Example1NoData(Program):
	
	FPS = 50
	STEPS_PER_FRAME = 80
	
	def create_sim_objects(self):
		# (radius, center, mass)
		ball1 = self.sim.add_sphere(0.1, (1,1 + 0.1,1), 1.0)
		ball2 = self.sim.add_sphere(0.1, (2,1.5 + 0.1,2), 1.0)
		ball3 = self.sim.add_sphere(0.1, (3,2 + 0.1,3), 1.0)
		
		print(self.sim.get_object(ball1).actor.set_color((1,1,1)))
		print(self.sim.get_object(ball2).actor.set_color((0,0.8,0.8)))
		print(self.sim.get_object(ball3).actor.set_color((0.7,0.5,0)))

if __name__ == '__main__':
	sim_program = Example1NoData()
	sim_program.start()