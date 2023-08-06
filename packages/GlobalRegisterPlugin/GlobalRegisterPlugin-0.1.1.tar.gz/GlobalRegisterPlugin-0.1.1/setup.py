from setuptools import setup

VERSION = '0.1.1'
PACKAGE = 'globalregister'

setup(
	name = 'GlobalRegisterPlugin',
	version = VERSION,
	description = "Displays a notice to the user that accounts are shared globally on the server.",
	author = 'Mitar',
	author_email = 'mitar.trac@tnode.com',
	url = 'http://mitar.tnode.com/',
	keywords = 'trac plugin',
	license = "AGPLv3",
	packages = [PACKAGE],
	include_package_data = True,
	install_requires = [],
	zip_safe = False,
	entry_points = {
		'trac.plugins': '%s = %s' % (PACKAGE, PACKAGE),
	},
)
