import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
	name = "liveconnect",
	version = "0.1.89",
	packages = find_packages(),
	install_requires = ['requests'],
	package_data = {
		'' : ['*.md']
	},
	author = "Samuel Lucidi",
	author_email = "mansam@csh.rit.edu",
	description = "LiveConnect OAuth adapter for Python",
	license = "MIT",
	keywords = "liveconnect skydrive",
	url = "http://github.com/mansam/liveconnect"
)
