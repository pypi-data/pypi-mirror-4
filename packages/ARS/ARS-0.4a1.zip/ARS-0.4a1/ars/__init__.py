# based on: ``django.__init__`` @ commit 5b644a5
# see its license in docs/Django BSD-LICENSE.txt
VERSION = (0, 4, 0, 'alpha', 1)  # i.e. 0.4a1


def get_version(*args, **kwargs):
	# Only import if it's actually called.
	from .utils.version import get_version
	return get_version(*args, **kwargs)
