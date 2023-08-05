from distutils.core import setup

setup(
	name = 'pyproxmox',
	version = '1.0.1',
	py_modules=['pyproxmox'],
	description = 'Python Wrapper for the Proxmox 2.x API',
	author = 'Toby Sears',
	author_email = 'admin@tobysears.co.uk',
	url = 'https://github.com/Daemonthread/pyproxmox',
	download_url = 'http://pypi.python.org/pypi/pyproxmox',
	keywords = ['proxmox','api'],
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Intended Audience :: Developers",
		"Intended Audience :: System Administrators",
		"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
	    "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
		],
	long_description = """
A python wrapper for the Proxmox 2.x API.

Example usage:

1) Create an instance of the prox_auth class by passing in the
url or ip of a server, username and password:

a = prox_auth('vnode01.example.org','apiuser@pve','examplePassword')

2) Create and instance of the pyproxmox class using the auth object as a parameter:

b = pyproxmox(a)

3) Run the pre defined methods of the pyproxmox class. NOTE: they all return data, usually in JSON format:

status = b.getClusterStatus()

For more information see https://github.com/Daemonthread/pyproxmox
"""
)
