
# Created on 2011.10.31
#
# @author: german

"""
ARS's exception class hierarchy.
"""

###############################################################################
# doc/python2.7/html/tutorial/errors.html#tut-userexceptions
# "When creating a module that can raise several distinct errors, a common
# practice is to create a base class for exceptions defined by that module, and
# subclass it to create specific exception classes for different error
# conditions."
###############################################################################


class ArsError(Exception):
	"""Base class for exceptions in this library.

	Attributes:
		msg  -- explanation of the error
	"""

	def __init__(self, msg=None):
		super(ArsError, self).__init__()
		self.msg = msg

class PhysicsEngineException(ArsError):
	"""Exception raised for errors in a physics engine.

	Attributes:
		msg  -- explanation of the error
	"""
	pass

class JointError(PhysicsEngineException):
	"""Exception raised for errors related to physical joints.

	Attributes:
		joint	-- joint in which the error occurred
		msg		-- explanation of the error
	"""

	def __init__(self, joint, msg=None):
		PhysicsEngineException.__init__(self, msg)
		self.joint = joint

class PhysicsObjectCreationError(PhysicsEngineException):
	"""Exception raised for errors in physics-engine objects creation.

	Attributes:
		type	-- type of the object being created
		msg		-- explanation of the error
	"""

	def __init__(self, type, msg=None):
		PhysicsEngineException.__init__(self, msg)
		self.type = type
