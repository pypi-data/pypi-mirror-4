from setuptools import setup

VERSION = '0.1.1'
PACKAGE = 'redirects'

setup(
	name = 'RedirectsPlugin',
	version = VERSION,
	description = "Define server-side redirects in Trac.",
	author = 'Mitar',
	author_email = 'mitar.trac@tnode.com',
	url = 'http://mitar.tnode.com/',
	keywords = 'trac plugin',
	license = "AGPLv3",
	packages = [PACKAGE],
    include_package_data = True,
    package_data = {
        PACKAGE: ['templates/*.html']
    },
	install_requires = [],
	zip_safe = False,
	entry_points = {
		'trac.plugins': '%s = %s' % (PACKAGE, PACKAGE),
	},
)
