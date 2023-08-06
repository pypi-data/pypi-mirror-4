import vtk

from .. import exceptions as exc
from .. import graphics as gp
from ..utils import geometry as gemut


class VtkAdapter(gp.Adapter):

	"""Graphics adapter to the Visualization Toolkit (VTK) library"""

	def __init__(
            self, title, pos=None, size=(1000, 600), zoom=1.0,
            cam_position=(10, 8, 10), background_color=(0.1, 0.1, 0.4),
            **kwargs):

		super(VtkAdapter, self).__init__()
		self.renderer = vtk.vtkRenderer()
		self.render_window = None
		self.interactor = None

		self._title = title
		self._size = size
		self._zoom = zoom
		self._cam_position = cam_position
		self._background_color = background_color

	def add_object(self, object_):
		self.renderer.AddActor(object_.actor)

	def remove_object(self, object_):
		self.renderer.RemoveActor(object_.actor)

	def start_window(self, on_idle_callback=None, on_reset_callback=None,
                     on_key_press_callback=None):
		# TODO: refactor according to restart_window(), reset() and the
		# desired behavior.
		self.on_idle_parent_callback = on_idle_callback
		self.on_reset_parent_callback = on_reset_callback
		self.on_key_press_parent_callback = on_key_press_callback

		# Create the RenderWindow and the RenderWindowInteractor and
		# link between them and the Renderer.
		self.render_window = vtk.vtkRenderWindow()
		self.interactor = vtk.vtkRenderWindowInteractor()
		self.render_window.AddRenderer(self.renderer)
		self.interactor.SetRenderWindow(self.render_window)

		# set properties
		self.renderer.SetBackground(self._background_color)
		self.render_window.SetSize(*self._size)
		self.render_window.SetWindowName(self._title)
		self.interactor.SetInteractorStyle(
			vtk.vtkInteractorStyleTrackballCamera())

		# create and configure a Camera, and set it as renderer's active one
		camera = vtk.vtkCamera()
		camera.SetPosition(self._cam_position)
		camera.Zoom(self._zoom)
		self.renderer.SetActiveCamera(camera)

		self.render_window.Render()

		# add observers to the RenderWindowInteractor
		self.interactor.AddObserver(gp.TIMER_EVENT, self._timer_callback)
		#noinspection PyUnusedLocal
		timerId = self.interactor.CreateRepeatingTimer(gp.TIMER_PERIOD)
		self.interactor.AddObserver(
			gp.KEY_PRESS_EVENT, self._key_press_callback)
		self.interactor.Start()

	def restart_window(self):
		# TODO: code according to start_window(), reset() and the desired behavior
		raise exc.ArsError()

	def finalize_window(self):
		"""Finalize and delete :attr:`renderer`, :attr:`render_window`
		and :attr:`interactor`.

		.. seealso::
			http://stackoverflow.com/questions/15639762/
			and
			http://docs.python.org/2/reference/datamodel.html#object.__del__

		"""
		self.render_window.Finalize()
		self.interactor.TerminateApp()

		# Instead of `del render_window, interactor` as would be done in a
		# script, this works too. Clearing `renderer` is not necessary to close
		# the window, just a good practice.
		self.renderer = None
		self.render_window = None
		self.interactor = None

	@staticmethod
	def _update_pose(obj, pos, rot):
		trans = gemut.Transform(pos, rot)
		vtk_tm = VtkAdapter._create_transform_matrix(trans)
		VtkAdapter._set_object_transform_matrix(obj, vtk_tm)

	def _timer_callback(self, obj, event):
		self.timer_count += 1
		if self.on_idle_parent_callback is not None:
			self.on_idle_parent_callback()
		iren = obj
		iren.GetRenderWindow().Render()  # same as self.render_window.Render()?

	def _key_press_callback(self, obj, event):
		"""
		obj: the vtkRenderWindowInteractor
		event: "KeyPressEvent"

		"""
		key = obj.GetKeySym().lower()
		if self.on_key_press_parent_callback:
			self.on_key_press_parent_callback(key)

	def reset(self):
		# remove all actors
		try:
			self.renderer.RemoveAllViewProps()
			self.interactor.ExitCallback()
		except AttributeError:
			pass
		#self.restartWindow()

	#===========================================================================
	# Functions and methods not overriding base class functions and methods
	#===========================================================================

	@staticmethod
	def _set_object_transform_matrix(obj, vtk_tm):
		"""Set ``obj``'s pose according to the transform ``vtk_tm``.

		:param obj: object to be modified
		:type obj: :class:`vtk.vtkProp3D`
		:param vtk_tm: homogeneous transform
		:type vtk_tm: :class:`vtk.vtkMatrix4x4`

		"""
		obj.PokeMatrix(vtk_tm)

	@staticmethod
	def _create_transform_matrix(trans):
		"""Create a homogeneous transform matrix valid for VTK.

		:param trans: homogeneous transform
		:type trans: :class:`ars.utils.geometry.Transform`
		:return: a VTK-valid transform matrix
		:rtype: :class:`vtk.vtkMatrix4x4`

		"""
		vtk_matrix = vtk.vtkMatrix4x4()
		vtk_matrix.DeepCopy(trans.get_long_tuple())

		return vtk_matrix


class VtkBody:

	adapter = VtkAdapter

	def __init__(self):
		self._actor = None

	def get_color(self):
		"""
		Returns the color of the body. If it is an assembly,
		it is not checked whether all the objects' colors are equal.

		"""
		# dealing with vtkAssembly properties is more complex
		if isinstance(self._actor, vtk.vtkAssembly):
			props_3D = self._actor.GetParts()
			props_3D.InitTraversal()
			actor_ = props_3D.GetNextProp3D()
			while actor_ is not None:
				self._color = actor_.GetProperty().GetColor()
				actor_ = props_3D.GetNextProp3D()
		else:
			self._color = self._actor.GetProperty().GetColor()
		return self._color

	def set_color(self, color):
		"""
		Sets the color of the body. If it is an assembly,
		all the objects' color is set.

		"""
		# dealing with vtkAssembly properties is more complex
		if isinstance(self._actor, vtk.vtkAssembly):
			props_3D = self._actor.GetParts()
			props_3D.InitTraversal()
			actor_ = props_3D.GetNextProp3D()
			while actor_ is not None:
				actor_.GetProperty().SetColor(color)
				actor_ = props_3D.GetNextProp3D()
		else:
			self._actor.GetProperty().SetColor(color)
		self._color = color


class Axes(VtkBody, gp.Axes):

	def __init__(self, pos=(0, 0, 0), rot=None, cylinder_radius=0.05):
		gp.Axes.__init__(self, pos, rot, cylinder_radius)

		# 2 different methods may be used here. See
		# http://stackoverflow.com/questions/7810632/

		axesActor = vtk.vtkAxesActor()
		axesActor.AxisLabelsOn()
		axesActor.SetShaftTypeToCylinder()
		axesActor.SetCylinderRadius(cylinder_radius)
		VtkAdapter._update_pose(axesActor, pos, rot)

		self._actor = axesActor


class Box(VtkBody, gp.Box):

	def __init__(self, size, pos, rot=None):
		gp.Box.__init__(self, size, pos, rot)

		box = vtk.vtkCubeSource()
		box.SetXLength(size[0])
		box.SetYLength(size[1])
		box.SetZLength(size[2])

		boxMapper = vtk.vtkPolyDataMapper()
		boxMapper.SetInputConnection(box.GetOutputPort())
		boxActor = vtk.vtkActor()

		VtkAdapter._update_pose(boxActor, pos, rot)
		boxActor.SetMapper(boxMapper)

		self._actor = boxActor


class Cone(VtkBody, gp.Cone):

	def __init__(self, height, radius, center, rot=None, resolution=20):
		gp.Cone.__init__(self, height, radius, center, rot, resolution)

		cone = vtk.vtkConeSource()
		cone.SetHeight(height)
		cone.SetRadius(radius)
		cone.SetResolution(resolution)
		# TODO: cone.SetDirection(*direction)
		# The vector does not have to be normalized

		coneMapper = vtk.vtkPolyDataMapper()
		coneMapper.SetInputConnection(cone.GetOutputPort())
		coneActor = vtk.vtkActor()

		VtkAdapter._update_pose(coneActor, center, rot)
		coneActor.SetMapper(coneMapper)

		self._actor = coneActor


class Sphere(VtkBody, gp.Sphere):

	"""
	VTK: sphere (represented by polygons) of specified radius centered at the
	origin. The resolution (polygonal discretization) in both the latitude
	(phi) and longitude (theta)	directions can be specified.

	"""

	def __init__(
            self, radius, center, rot=None, phi_resolution=20,
            theta_resolution=20):
		gp.Sphere.__init__(
            self, radius, center, rot, phi_resolution, theta_resolution)

		sphere = vtk.vtkSphereSource()
		sphere.SetRadius(radius)
		sphere.SetPhiResolution(phi_resolution)
		sphere.SetThetaResolution(theta_resolution)

		sphereMapper = vtk.vtkPolyDataMapper()
		sphereMapper.SetInputConnection(sphere.GetOutputPort())
		sphereActor = vtk.vtkActor()

		VtkAdapter._update_pose(sphereActor, center, rot)
		sphereActor.SetMapper(sphereMapper)

		self._actor = sphereActor


class Cylinder(VtkBody, gp.Cylinder):

	def __init__(self, length, radius, center, rot=None, resolution=20):
		gp.Cylinder.__init__(self, length, radius, center, rot, resolution)

		# VTK: The axis of the cylinder is aligned along the global y-axis.
		cyl = vtk.vtkCylinderSource()
		cyl.SetHeight(length)
		cyl.SetRadius(radius)
		cyl.SetResolution(resolution)

		# set it to be aligned along the global Z-axis, ODE-like
		userTransform = vtk.vtkTransform()
		userTransform.RotateX(90.0)
		# TODO: add argument to select the orientation axis, like
		# cylDirection in Mass.setCylinder()
		transFilter = vtk.vtkTransformPolyDataFilter()
		transFilter.SetInputConnection(cyl.GetOutputPort())
		transFilter.SetTransform(userTransform)

		cylMapper = vtk.vtkPolyDataMapper()
		cylMapper.SetInputConnection(transFilter.GetOutputPort())
		cylActor = vtk.vtkActor()

		VtkAdapter._update_pose(cylActor, center, rot)
		cylActor.SetMapper(cylMapper)

		self._actor = cylActor


class Capsule(VtkBody, gp.Capsule):

	def __init__(self, length, radius, center, rot=None, resolution=20):
		gp.Capsule.__init__(self, length, radius, center, rot, resolution)
		# TODO: simplify this construction using those corresponding to
		# Cylinder and Sphere?

		sphere1 = vtk.vtkSphereSource()
		sphere1.SetRadius(radius)
		sphere1.SetPhiResolution(resolution)
		sphere1.SetThetaResolution(resolution)
		sphereMapper1 = vtk.vtkPolyDataMapper()
		sphereMapper1.SetInputConnection(sphere1.GetOutputPort())
		sphereActor1 = vtk.vtkActor()
		sphereActor1.SetMapper(sphereMapper1)
		sphereActor1.SetPosition(0, 0, -length / 2.0)

		sphere2 = vtk.vtkSphereSource()
		sphere2.SetRadius(radius)
		sphere2.SetPhiResolution(resolution)
		sphere2.SetThetaResolution(resolution)
		sphereMapper2 = vtk.vtkPolyDataMapper()
		sphereMapper2.SetInputConnection(sphere2.GetOutputPort())
		sphereActor2 = vtk.vtkActor()
		sphereActor2.SetMapper(sphereMapper2)
		sphereActor2.SetPosition(0, 0, length / 2.0)

		# set it to be aligned along the global Z-axis, ODE-like
		cylinder = vtk.vtkCylinderSource()
		cylinder.SetRadius(radius)
		cylinder.SetHeight(length)
		cylinder.SetResolution(resolution)

		userTransform = vtk.vtkTransform()
		userTransform.RotateX(90.0)
		# TODO: add argument to select the orientation axis, like
		# cylDirection in Mass.setCylinder()
		transFilter = vtk.vtkTransformPolyDataFilter()
		transFilter.SetInputConnection(cylinder.GetOutputPort())
		transFilter.SetTransform(userTransform)

		cylinderMapper = vtk.vtkPolyDataMapper()
		cylinderMapper.SetInputConnection(transFilter.GetOutputPort())
		cylinderActor = vtk.vtkActor()
		cylinderActor.SetMapper(cylinderMapper)

		assembly = vtk.vtkAssembly()
		assembly.AddPart(cylinderActor)
		assembly.AddPart(sphereActor1)
		assembly.AddPart(sphereActor2)

		VtkAdapter._update_pose(assembly, center, rot)
		self._actor = assembly


class Trimesh(VtkBody, gp.Trimesh):

	def __init__(self, vertices, faces, pos, rot=None):
		gp.Trimesh.__init__(self, vertices, faces, pos, rot)

		# create points
		points = vtk.vtkPoints()
		triangles = vtk.vtkCellArray()
		triangle_list = []

		for face in faces:
			# get the 3 points of each face
			p_id = points.InsertNextPoint(*vertices[face[0]])
			points.InsertNextPoint(*vertices[face[1]])
			points.InsertNextPoint(*vertices[face[2]])

			# the triangle is defined by 3 points
			triangle = vtk.vtkTriangle()
			triangle.GetPointIds().SetId(0, p_id)       # point 0
			triangle.GetPointIds().SetId(1, p_id + 1)   # point 1
			triangle.GetPointIds().SetId(2, p_id + 2)   # point 2
			triangle_list.append(triangle)

		# insert each triangle into the Vtk data structure
		for triangle in triangle_list:
			triangles.InsertNextCell(triangle)

		# polydata object: represents a geometric structure consisting of
		# vertices, lines, polygons, and/or triangle strips
		trianglePolyData = vtk.vtkPolyData()
		trianglePolyData.SetPoints(points)
		trianglePolyData.SetPolys(triangles)

		# mapper
		mapper = vtk.vtkPolyDataMapper()
		mapper.SetInput(trianglePolyData)

		# actor: represents an object (geometry & properties) in a rendered scene
		triangles_actor = vtk.vtkActor()
		VtkAdapter._update_pose(triangles_actor, pos, rot)
		triangles_actor.SetMapper(mapper)

		self._actor = triangles_actor


class ScreenshotRecorder(gp.ScreenshotRecorder):

	"""
	Based on an official example script, very simple:
	http://www.vtk.org/Wiki/VTK/Examples/Python/Screenshot

	"""

	def __init__(self, base_filename='screenshot_', graphics_adapter=None):
		self.base_filename = base_filename
		self.gAdapter = graphics_adapter
		self.last_write_time = None
		self.period = None

	def write(self, index=1, time=None):
		"""
		Writes the current image displayed in the render window as a PNG file
		named 'self.base_filename' with	the 'index' number appended, and a
		'.png' extension.

		"""
		# TODO: see if the workaround (get render_window and create
		# image_getter every time) was needed because we used
		# image_getter.SetInput instead of SetInputConnection.
		render_window = self.gAdapter.render_window
		image_getter = vtk.vtkWindowToImageFilter()
		image_getter.SetInput(render_window)
		image_getter.Update()

		writer = vtk.vtkPNGWriter()
		writer.SetFileName('%s%d.png' % (self.base_filename, index))
		writer.SetInputConnection(image_getter.GetOutputPort())
		writer.Write()

		if time is not None:
			self.last_write_time = time
