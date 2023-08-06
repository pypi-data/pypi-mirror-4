from __future__ import unicode_literals

import datetime
import subprocess


def get_version(version=None, length='full'):
	"""Return a PEP 386-compliant version number from ``version``.

	:param version: the value to format, expressed as a tuple of strings, of
		length 5, with the element before last (i.e. version[3]) equal to
		any of the following: ``('alpha', 'beta', 'rc', 'final')``
	:type version: tuple of strings
	:param length: the format of the returned value, equal to any of
		the following: ``('short', 'medium', 'full')``
	:type length: basestring
	:return: version as a string
	:rtype: str

	>>> get_version(version=(0, 4, 0, 'alpha', 0))
	0.4.dev20130401011455
	>>> get_version(version=(0, 4, 0, 'alpha', 1))
	0.4a1
	>>> get_version(version=(0, 4, 1, 'alpha', 0))
	0.4.1.dev20130401011455
	>>> get_version(version=(0, 4, 1, 'alpha', 1))
	0.4.1a1
	>>> get_version(version=(0, 4, 0, 'beta', 0))
	0.4b0
	>>> get_version(version=(0, 4, 0, 'rc', 0))
	0.4c0
	>>> get_version(version=(0, 4, 0, 'final', 0))
	0.4
	>>> get_version(version=(0, 4, 0, 'final', 1))
	0.4
	>>> get_version(version=(0, 4, 1, 'final', 0))
	0.4.1

	>>> get_version(version=(0, 4, 0, 'alpha', 0), length='medium')
	0.4.dev
	>>> get_version(version=(0, 4, 0, 'alpha', 0), length='short')
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
		return str(main)

	sub = ''
	if version[3] == 'alpha' and version[4] == 0:
		hg_timestamp = get_hg_tip_timestamp()
		if length == 'full':
			if hg_timestamp:
				sub = '.dev%s' % hg_timestamp
		else:
			sub = '.dev'

	elif version[3] != 'final':
		mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
		sub = mapping[version[3]] + str(version[4])
	return str(main + sub)


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


def get_hg_tip_timestamp():
	"""Return a numeric identifier of the latest changeset of the current
	repository based on its timestamp.

	To obtain the value it runs the command ``hg tip --template '{date}'``

	>> get_hg_tip_timestamp()
	'20130328021918'

	Based on: ``django.utils.get_git_changeset`` @ 1.5.0
	(see its license in docs/Django BSD-LICENSE.txt) and
	http://hgbook.red-bean.com/read/customizing-the-output-of-mercurial.html

	"""
	# Timestamp conversion process:
	# '1364437158.010800'
	# datetime.datetime(2013, 3, 28, 2, 19, 18, 10800)
	# '20130328021918'

	pipe = subprocess.Popen(
		['hg', 'tip', '--template', '{date}'],  # don't use "'{date}'"
		stdout=subprocess.PIPE)
	timestamp = pipe.stdout.read()

	try:
		timestamp = datetime.datetime.utcfromtimestamp(float(timestamp))
	except ValueError:
		return None
	return timestamp.strftime('%Y%m%d%H%M%S')
