import setuptools


requires = [
]


setuptools.setup(
	name = 'bold',
	version = '0.1',
	description = 'build tool',
	author = 'fillest',
	author_email = 'fsfeel@gmail.com',
	url = 'https://github.com/fillest/bold',
	package_dir = {'': 'src'},
	packages = setuptools.find_packages('src'),
	include_package_data = True,
	zip_safe = False,
	install_requires = requires,
)
