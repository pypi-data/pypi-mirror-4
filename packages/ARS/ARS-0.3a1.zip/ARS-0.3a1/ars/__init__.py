# based on: ``django.__init__`` @ commit 5b644a5
# see its license in docs/Django BSD-LICENSE.txt
VERSION = (0, 3, 0, 'alpha', 1)


def get_version(*args, **kwargs):
	# Only import if it's actually called.
	from ars.utils.version import get_version
	return get_version(*args, **kwargs)
