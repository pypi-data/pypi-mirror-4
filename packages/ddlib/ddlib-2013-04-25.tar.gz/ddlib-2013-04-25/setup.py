from distutils.core import setup

setup(
	name='ddlib',
	version='2013-04-25',
	description='A set of common functions by DDarko.org',
	long_description = open('README').read(),
	author='DDarko.org',
	author_email='dd@ddarko.org',
	license='MIT http://www.opensource.org/licenses/mit-license.php',
	url='',
	platforms = ['any'],
	packages=['ddlib'],
	keywords=['Python', 'ddlib', 'ddarko'],
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Intended Audience :: Developers',
		'Environment :: Console',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.5',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.0',
		'Programming Language :: Python :: 3.1',
		'Programming Language :: Python :: 3.2',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
)

'''
test_suite='testsuite',
entry_points="""
[console_scripts]
cmd = package:main
""",
'''