import subprocess


def get_version(version=None, length='full'):
	"""Returns a (almost?) PEP 386-compliant version number from `version`.

	>>> get_version(version=(0,4,0,'alpha',0))
	0.4.dev1a4b04cf687a
	>>> get_version(version=(0,4,0,'alpha',0))
	0.4.dev1a4b04cf687a+
	>>> get_version(version=(0,4,0,'alpha',0), length='medium')
	0.4.dev
	>>> get_version(version=(0,4,0,'alpha',0), length='short')
	0.4

	based on: ``django.utils.version`` @ commit 9098504.
	See its license in docs/Django BSD-LICENSE.txt

	"""
	assert length in ('short', 'medium', 'full')

	if version is None:
		from ars import VERSION as version
	else:
		assert len(version) == 5
		assert version[3] in ('alpha', 'beta', 'rc', 'final')

	# Now build the two parts of the version number:
	# main = X.Y[.Z]
	# sub = .devN - for pre-alpha releases
	#     | {a|b|c}N - for alpha, beta and rc releases

	parts = 2 if version[2] == 0 else 3
	main = '.'.join(str(x) for x in version[:parts])

	if length == 'short':
		return main

	sub = ''
	if version[3] == 'alpha' and version[4] == 0:
		hg_changeset = get_hg_changeset()
		if length == 'full':
			if hg_changeset:
				sub = '.dev%s' % hg_changeset
		else:
			sub = '.dev'

	elif version[3] != 'final':
		mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
		sub = mapping[version[3]] + str(version[4])
	return main + sub


def get_hg_changeset():
	"""Return the global revision id that identifies the working copy.

	To obtain the value it runs the command ``hg identify --id``, whose short
	form is ``hg id -i``.

	>>> get_hg_changeset()
	1a4b04cf687a
	>>> get_hg_changeset()
	1a4b04cf687a+

	.. note::
	   When there are outstanding (i.e. uncommitted) changes in the working
	   copy, a ``+`` character will be appended to the current revision id.

	"""
	pipe = subprocess.Popen(['hg', 'identify', '--id'], stdout=subprocess.PIPE)
	changeset = pipe.stdout.read()
	#return changeset.strip().strip('+')
	return changeset.strip()

