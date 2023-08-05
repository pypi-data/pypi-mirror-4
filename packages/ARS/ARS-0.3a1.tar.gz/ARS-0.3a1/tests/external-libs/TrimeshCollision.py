#!/usr/bin/env python

# Created on 2012.01.15
#
# @author: german

# TODO: update the rotation in the visualization

"""
Tests the collision of an sphere with a trimesh.
It does NOT use ARS or depend on it in any way.
"""

import math
from random import random, choice

import ode
import vtk

TIMER_PERIOD = 50 # milliseconds
TIMER_EVENT = 'TimerEvent'
win_size = (1000,600)
cam_position = (30,10,50)

tm_resolution = 1.0
tm_x, tm_z = (40,40)

ball_body = None
ball_source = None
ball_actor = None
ball_center = (9,7,5)
ball_radius = 1.0
ball_mass_value = 1.0

fps = 50
dt = 1.0 / fps
stepsPerFrame = 100
paused = False
simTime = 0.0
numIter = 0

world = None
space = None
floor = None
contactGroup = ode.JointGroup()

def nearCallback(args, geom1, geom2):
	"""Callback function for the collide() method. This function checks if the
	given geoms do collide and creates contact joints if they do."""
	contactJointBounce = 0.2
	contactJointMu = 500 # 0-5 = very slippery, 50-500 = normal, 5000 = very sticky

	if ode.areConnected(geom1.getBody(), geom2.getBody()):
		return

	# create contact joints
	world, contactgroup = args

	# check if the objects collide
	contacts = ode.collide(geom1, geom2)
	for c in contacts:

		(pos, normal, depth, geom1, geom2) = c.getContactGeomParams()
		print((pos, normal, depth))

		c.setBounce(contactJointBounce)
		c.setMu(contactJointMu)
		j = ode.ContactJoint(world, contactgroup, c)
		j.attach(geom1.getBody(), geom2.getBody())

def createOdeWorld(gravity=(0.0,-9.81,0.0), erp=0.8, cfm=1E-4):
	# create an ODE world object
	world = ode.World()
	world.setGravity(gravity)
	world.setERP(erp)
	world.setCFM(cfm)
	return world

def constant_heightfield(num_x, num_z, height=0.0):
	"""A height field where all the values are the same"""
	# that x and z are integers, not floats, does not matter
	verts=[]
	for x in range(num_x):
		for z in range(num_z):
			verts.append((x, height, z))
	return verts

def random_heightfield(num_x, num_z, scale=1.0):
	"""Based on 'Edward Dale - Snowballs: An experiment in Winter frivolity
	(2006).' http://goo.gl/cyaZs
	A height field where values are completely random."""
	# that x and z are integers, not floats, does not matter
	verts=[]
	for x in range(num_x):
		for z in range(num_z):
			verts.append( (x,random()*scale,z) )
	return verts

def sinusoidal_heightfield(num_x, num_z, height_scale=1.0, frequency_x=1.0):
	"""Creates the vertices corresponding to a sinusoidal heightfield along the
	X axis. The height_scale controls the amplitude of the wave, and
	frequency_x its frequency."""
	# TODO: fix the frequency units
	verts=[]
	for x in range(num_x):
		for z in range(num_z):
			verts.append( (x, math.sin(x * frequency_x)*height_scale, z) )
	return verts

def get_faces(num_x, num_z):
	"""Based on 'Edward Dale - Snowballs: An experiment in Winter frivolity
	(2006).' http://goo.gl/cyaZs
	A height field is rectilinear, but the faces are only going to be
	triangular. This method chooses 3 vertices out of each 4 to make a face and
	the other set to make another triangular face. This is done randomly to
	eliminate artifacts."""
	faces=[]
	for z in range(num_z-1):
		for x in range(num_x-1):
			one = (num_x*z)+x
			two = (num_x*z)+x+1
			three = (num_x*(z+1))+x
			four = (num_x*(z+1))+x+1
			faces += choice( ( [( three,two,one ),( three,four,two )],
							[( four,two,one ), ( three,four,one )] ) )
			# randomness does not seem to help in any way
			# faces += [( three,two,one ),( three,four,two )] #( three,two,one )
	return faces

#noinspection PyUnusedLocal
def timerCallback(obj, event):
	performSimStepsPerFrame()
	pos = ball_body.getPosition()
	ball_actor.SetPosition(*pos)

	iren = obj
	iren.GetRenderWindow().Render()

def performSimStepsPerFrame():

	global stepsPerFrame, world, contactGroup, numIter, simTime

	for i in range(stepsPerFrame): #@UnusedVariable
		# Detect collisions and create contact joints
		space.collide((world, contactGroup), nearCallback)

		# Simulation step
		timeStep = dt / stepsPerFrame
		world.step(timeStep)
		simTime += timeStep
		numIter += 1

		# Remove all contact joints
		contactGroup.empty()

def swap_faces_indices(faces):
	"""Faces had to change their indices to work with ODE. With the initial
	'get_faces', the normal to the triangle defined by the 3 vertices pointed
	(following the right-hand rule) downwards. Swapping the third with the
	first index, now the triangle normal pointed upwards."""

	new_faces = []
	for face in faces:
		new_faces.append((face[2], face[1], face[0]))
	return new_faces

if __name__ == '__main__':

	world = createOdeWorld()
	space = ode.Space()

	#===========================================================================
	# Ball (ODE)
	#===========================================================================

	ball_body = ode.Body(world)
	ball_mass = ode.Mass()
	ball_mass.setSphereTotal(ball_mass_value, ball_radius)
	ball_body.setMass(ball_mass)
	ball_geom = ode.GeomSphere(space, ball_radius)
	ball_geom.setBody(ball_body)
	ball_body.setPosition(ball_center)

	#===========================================================================
	# Trimesh (ODE)
	#===========================================================================

	#tm_verts = constant_heightfield(tm_x, tm_z, height=0.0)
	#tm_verts = random_heightfield(tm_x, tm_z, 2.0)
	tm_verts = sinusoidal_heightfield(tm_x, tm_z, height_scale=2.0, frequency_x=0.5)
	tm_faces = get_faces(int(tm_resolution) * tm_x, int(tm_resolution) * tm_z)
	tm_faces = swap_faces_indices(tm_faces)

	print('vertices')
	print(tm_verts)
	print('faces')
	print(tm_faces)

	tm_data = ode.TriMeshData()
	tm_data.build(tm_verts, tm_faces)
	tm = ode.GeomTriMesh(tm_data, space)

	#===========================================================================
	# VTK
	#===========================================================================
	# create a rendering window and renderer
	ren = vtk.vtkRenderer()
	renWin = vtk.vtkRenderWindow()
	renWin.AddRenderer(ren)
	renWin.SetSize(win_size)
	ren.GetActiveCamera().SetPosition(cam_position)

	# create a renderwindowinteractor
	iren = vtk.vtkRenderWindowInteractor()
	iren.SetRenderWindow(renWin)
	iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

	#===========================================================================
	# Draw triangles
	#===========================================================================
	# create points
	points = vtk.vtkPoints()
	triangles = vtk.vtkCellArray()
	triangle_list = []

	for face in tm_faces:
		p_id = points.InsertNextPoint(*tm_verts[face[0]])
		points.InsertNextPoint(*tm_verts[face[1]])
		points.InsertNextPoint(*tm_verts[face[2]])

		triangle1 = vtk.vtkTriangle()
		triangle1.GetPointIds().SetId(0, p_id)
		triangle1.GetPointIds().SetId(1, p_id + 1)
		triangle1.GetPointIds().SetId(2, p_id + 2)
		triangle_list.append(triangle1)

	for triangle in triangle_list:
		triangles.InsertNextCell(triangle)

	# polydata object
	trianglePolyData = vtk.vtkPolyData()
	trianglePolyData.SetPoints(points)
	trianglePolyData.SetPolys(triangles)

	# mapper
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInput(trianglePolyData)

	# actor
	triangles_actor = vtk.vtkActor()
	triangles_actor.SetMapper(mapper)
	ren.AddActor(triangles_actor)

	#===========================================================================
	# draw sphere
	#===========================================================================

	ball_source = vtk.vtkSphereSource()
	ball_source.SetRadius(ball_radius)
	# do NOT use ball_source.SetCenter(ball_center)
	ball_source.SetPhiResolution(20) # looks more sphere-like
	ball_source.SetThetaResolution(20)
	ball_mapper = vtk.vtkPolyDataMapper()
	ball_mapper.SetInputConnection(ball_source.GetOutputPort())
	ball_actor = vtk.vtkActor()
	ball_actor.SetMapper(ball_mapper)
	ren.AddActor(ball_actor)

	#===========================================================================
	# start visualization
	#===========================================================================
	# enable user interface interactor
	iren.Initialize()
	renWin.Render()
	iren.AddObserver(TIMER_EVENT, timerCallback)
	timerId = iren.CreateRepeatingTimer(TIMER_PERIOD)
	iren.Start()
	print('done')
	print('simTime: %f, numIter: %d' % (simTime, numIter))
