import setuptools


requirements = [
]

#py2.6 has no argparse
try: 
	import argparse
except ImportError:
	requirements.append('argparse')


setuptools.setup(
	name = 'bold',
	version = '0.2.0',
	description = 'A software build automation tool',
	long_description = 'A software build automation tool',
	author = 'Philipp Saveliev',
	author_email = 'fsfeel@gmail.com',
	url = 'https://github.com/fillest/bold',
	package_dir = {'': 'src'},
	packages = setuptools.find_packages('src'),
	include_package_data = True,
	zip_safe = False,
	install_requires = requirements,
	license = "The MIT License (http://www.opensource.org/licenses/mit-license.php)",
	classifiers = [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',
		'Topic :: Utilities',
		'Environment :: Console',
	],
	entry_points = """
		[console_scripts]
			bold = bold:run
	""",
)
