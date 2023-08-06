"""Runs the simplest simulation ever: a falling ball impacts the floor.

"""
from ars.app import Program


class FallingBall(Program):

	def create_sim_objects(self):
		self.sim.add_sphere(0.5, (1,10,1), density=1) # radius, center, density
