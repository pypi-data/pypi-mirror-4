========================================
Autonomous Robot Simulator (ARS)
========================================

ARS is a physically-accurate open-source simulation suite for research and
development of mobile manipulators and, in general, any multi-body system. It
is modular, easy to learn and use, and can be a valuable tool in the process
of robot design, in the development of control and reasoning algorithms, as
well as in teaching and educational activities.

It will encompass a wide range of tools spanning from kinematics and dynamics
simulation to robot interfacing and control.

The software is implemented in Python integrating the
`Open Dynamics Engine (ODE) <https://sourceforge.net/projects/opende/>`_
and the `Visualization Toolkit (VTK) <http://www.vtk.org/>`_.

Installation and Requirements
====================
For installation instructions and requirements, see the
`online documentation <http://ars-project.readthedocs.org/en/latest/installation/>`_.

ARS relies in these software:

* Python 2.7
* ODE (Open Dynamics Engine) 0.12 (from rev 1864 could work but is untested) with Python bindings
* VTK (Visualization Toolkit) 5.8 with Python bindings
* NumPy 1.6

Documentation
====================
The documentation is hosted at
`ReadTheDocs.org <http://ars-project.readthedocs.org>`_
and it is generated dynamically after each commit to the repository.

License
==========
This software is licensed under the OSI-approved "BSD License". To avoid
confusion with the original BSD license from 1990, the FSF refers to it as
"Modified BSD License". Other names include "New BSD", "revised BSD", "BSD-3",
or "3-clause BSD".

See the included LICENSE.txt file.

Tests
==========
To run the included test suite (provided you have ``mock`` installed)::

   ~/ars$ python -m unittest discover --verbose

If the output is too verbose for your taste, remove the option ``--verbose``.
