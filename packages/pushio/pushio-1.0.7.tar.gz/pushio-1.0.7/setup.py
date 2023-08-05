from distutils.core import setup
setup(
	name = 'pushio',
	packages = ['pushio'],
	version = '1.0.7',
	description = 'Push IO push notification service library',
	author='Push IO LLC',
	author_email = "info@push.io",
	url = "http://www.push.io/",
	download_url = "http://pypi.python.org/packages/source/p/pushio/pushio-1.0.7.tar.gz",
	keywords = ["pushio", "push", "notifications"],
	requires = ["json", "urllib"],
	provides = ["pushio"],
	license = "BSD License",
	classifiers = [
	   	"Programming Language :: Python",
		"Programming Language :: Python :: 2",
	        "Programming Language :: Python :: 3",
        	"Development Status :: 4 - Beta",
		"Environment :: Web Environment",
		"Intended Audience :: Developers",
		"Topic :: Internet :: WWW/HTTP",
		"License :: OSI Approved :: BSD License",	
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Other/Nonlisted Topic",
        ],
    long_description = """\
Push IO push notification module
--------------------------------
This library makes it easy to send push notifications via the Push IO service.

This version requires Python 2 or later.
"""
)
