#!/usr/bin/env python
"""Display a list of all demos and let user run them individually.

"""
from importlib import import_module
import sys


DEMOS_PACKAGE_PREFIX = 'demos'
DEMOS = [
	# (module, class_name),

	('CentrifugalForceTest', 'CentrifugalForceTest'),
	('ControlledSimpleArm', 'ControlledSimpleArm'),
	('FallingBall', 'FallingBall'),
	('FallingBalls', 'FallingBalls'),
	('SimpleArm', 'SimpleArm'),
	('Vehicle1', 'Vehicle1'),
	('Vehicle2', 'Vehicle2'),
	('Vehicle2WithScreenshots', 'Vehicle2WithScreenshots'),
	('VehicleWithArm', 'VehicleWithArm'),
	('VehicleWithControlledArm', 'VehicleWithControlledArm'),

	('IROS.example1_bouncing_ball', 'Example1'),
	('IROS.example1_bouncing_balls-no_data', 'Example1NoData'),
	('IROS.example2_conical_pendulum', 'Example2'),
	('IROS.example3_speed_profile', 'Example3'),
	('IROS.example4_sinusoidal_terrain', 'Example4'),
	('IROS.example4b_sinusoidal_terrain_with_screenshot_recorder', 'Example4SR'),
	('IROS.example5_vehicle_with_user_input', 'Example5'),

	('sensors.accelerometer1', 'Accelerometer'),
	('sensors.accelerometer2', 'Accelerometer'),
	('sensors.body', 'GPSSensor'),
	('sensors.joint_power1', 'JointPower'),
	('sensors.joint_torque1', 'JointTorque'),
	('sensors.kinetic_energy1', 'KineticEnergy'),
	('sensors.laser', 'LaserSensor'),
	('sensors.laser', 'VisualLaser'),
	('sensors.potential_energy1', 'PotentialEnergy'),
	('sensors.rotary_joint', 'RotaryJointSensor'),
	('sensors.system_total_energy1', 'SystemTotalEnergy'),
	('sensors.total_energy1', 'TotalEnergy'),
	('sensors.velometer1', 'Velometer'),
]

INTRODUCTION_MSG = """
This executable can run all the demos included in ARS.
"""
INSTRUCTIONS = """
Enter one of the following values:
   d:         print demo list
   (number):  run a demo (patience, the first time takes it takes a while)
   q:         quit
"""

QUIT_STR = 'q'


def show_demo_list():
	for i, option in enumerate(DEMOS):
		print('%s: %s' % (i, option))


def run_demo(selection):
	try:
		selected_demo_index = int(selection)
	except ValueError:
		print('Error, invalid input')
		return 1

	try:
		selected_demo = DEMOS[selected_demo_index]  # (module, class_name)
	except IndexError:
		print('Error, option number is out of range')
		return 2
	module = import_module(DEMOS_PACKAGE_PREFIX + '.' + selected_demo[0])
	klass = getattr(module, selected_demo[1])

	sim_program = klass()
	sim_program.start()
	try:
		sim_program.print_final_data()
	except AttributeError:
		pass
	sim_program.finalize()


def main():
	user_input = None
	print(INTRODUCTION_MSG)

	while True:
		print(INSTRUCTIONS)
		user_input = raw_input('value: ')
		user_input = user_input.strip().lower()

		if user_input == 'd':
			show_demo_list()

		elif user_input == QUIT_STR:
			print('Bye')
			return 0

		else:
			run_demo(user_input)

if __name__ == '__main__':
	exit_value = main()
	sys.exit(exit_value)
