"""Runs a very simple simulation: three falling balls impact the floor.

"""
from ars.app import Program


class FallingBalls(Program):

	def create_sim_objects(self):
		self.sim.add_sphere(0.3, (1,6,1), density=1) # radius, center, density
		self.sim.add_sphere(0.5, (2,4,2), density=0.5)
		self.sim.add_sphere(0.2, (3,2,3), mass=5) # radius, center, mass
