import os, sys

base_dir = 'C:\\VTK-5.4.2-with-python\\'
sys.path.append(os.path.dirname(base_dir + 'bin\\'))
sys.path.append(os.path.dirname(base_dir + 'lib\\site-packages\\'))

import vtk

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

ball_source = vtk.vtkSphereSource()
ball_source.SetRadius(1.0) # necessary?
ball_mapper = vtk.vtkPolyDataMapper()
ball_mapper.SetInputConnection(ball_source.GetOutputPort())
ball_actor = vtk.vtkActor()
ball_actor.SetMapper(ball_mapper)

ren.AddActor(ball_actor)
iren.Initialize()
renWin.Render()
iren.Start()

# press 'e' (with focus on the visualization window) to exit