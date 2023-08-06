from setuptools import setup

VERSION = '0.1.2'
PACKAGE = 'publicnotifications'

setup(
	name = 'PublicNotificationsPlugin',
	version = VERSION,
	description = "Allow to define CC address(es) used only for public tickets notifications.",
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
