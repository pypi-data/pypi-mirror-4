
# Created on 2012.01.07
#
# @author: german

from ars.graphics.adapters import vtk, VtkAdapter, Axes, Box, Capsule, Cone, Cylinder, Sphere
from ars.graphics.adapters import ScreenshotRecorder

def test_adapter_and_objects():
	gAdapter = VtkAdapter()
	gAdapter.create_window("test")
	
	axes1 = Axes()
	axes2 = Axes(cylinder_radius=0.02)
	box = Box(size=(0.5,1.0,2.0), position=(2,2,2))
	cone = Cone(1.0, 0.2, center=(1,1,1))
	sphere = Sphere(0.5, center=(-2,-2,-2))
	cyl = Cylinder(length=2, radius=0.25, center=(1,-1,1)) #, orientation=(mut.pi/3,mut.pi/3,mut.pi/3))
	caps = Capsule(length=2, radius=0.25, center=(-1,-1,-1)) 
	
	gAdapter.add_object(axes1)
	gAdapter.add_object(axes2)
	gAdapter.add_object(box)
	gAdapter.add_object(cone)
	gAdapter.add_object(sphere)
	gAdapter.add_object(cyl)
	gAdapter.add_object(caps)
	
	# initialized as identity matrix
	vtk_matrix1 = vtk.vtkMatrix4x4()
	vtk_matrix2 = vtk.vtkMatrix4x4()
	vtk_matrix3 = vtk.vtkMatrix4x4()
	#_values = gut.nestedIterable2tuple(iterable_)
	#vtk_matrix.DeepCopy(_values)

	# translation
	vtk_matrix1.Identity()
	vtk_matrix1.SetElement(0, 3, 1)
	vtk_matrix1.SetElement(1, 3, 0)
	vtk_matrix1.SetElement(2, 3, 4)
	
	# axes permutation
	vtk_matrix2.Zero(); vtk_matrix2.SetElement(3, 3, 1) # don't forget to set the lower left corner value!
	vtk_matrix2.SetElement(0, 2, 1)
	vtk_matrix2.SetElement(1, 0, 1)
	vtk_matrix2.SetElement(2, 1, 1)
	
	# corresponds to a rotation -74 degrees aprox. around the axis 1/3*(-1,2,2)
	vtk_matrix3.SetElement(0, 0, 0.36)
	vtk_matrix3.SetElement(0, 1, 0.48)
	vtk_matrix3.SetElement(0, 2, -0.8)
	vtk_matrix3.SetElement(1, 0, -0.8)
	vtk_matrix3.SetElement(1, 1, 0.60)
	vtk_matrix3.SetElement(1, 2, 0)
	vtk_matrix3.SetElement(2, 0, 0.48)
	vtk_matrix3.SetElement(2, 1, 0.64)
	vtk_matrix3.SetElement(2, 2, 0.60)
	
	#box.bodyObject.SetUserMatrix(vtk_matrix) # concatenates the transform
	sphere.actor.PokeMatrix(vtk_matrix1) # sets the final transform
	cone.actor.PokeMatrix(vtk_matrix2)
	axes1.actor.PokeMatrix(vtk_matrix3)
	caps.actor.PokeMatrix(vtk_matrix3)
	
	gAdapter.start_window()

def test_screenshot_recorder():
	
	global i
	gAdapter = VtkAdapter()
	gAdapter.create_window("test")
	sphere = Sphere(0.5, center=(-2,-2,-2))
	gAdapter.add_object(sphere)
	
	#recorder = ScreenshotRecorder()
	recorder = ScreenshotRecorder('test', gAdapter)
	i = 0

	#noinspection PyUnusedLocal
	def on_key_press(key):
		global i
		#recorder.set_input(gAdapter.renWin)
		i += 1
		recorder.write(i)
	
	gAdapter.start_window(on_key_press_callback=on_key_press)

if __name__ == '__main__':
	test_adapter_and_objects()
	test_screenshot_recorder()