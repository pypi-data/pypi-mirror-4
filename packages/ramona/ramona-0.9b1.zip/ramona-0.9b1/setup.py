from distutils.core import setup

# See http://guide.python-distribute.org/
# See http://docs.python.org/distutils/setupscript.html

setup(
	name='ramona',
	description='Enterprise-grade runtime supervisor',
	author='Ales Teska',
	author_email='ales.teska+ramona@gmail.com',
	version='0.9b1', # Also in ramona.__init__.py (+ relevant version format specification)
	packages=['ramona','ramona.server','ramona.console','ramona.console.cmd','ramona.httpfend'],
	license='BSD 2-clause "Simplified" License',
	long_description=open('README').read(),
	url='https://github.com/ateska/ramona',
	requires="pyev",
	package_data={
		'ramona.httpfend': [
			'*.html',
			'static/jquery/*.js',
			'static/bootstrap/js/*.js',
			'static/bootstrap/css/*.css',
			'static/bootstrap/img/*.png',
			'static/img/*.gif',
			'static/img/*.ico',
			]
	},
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: BSD License',
		'Natural Language :: English',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX',
		'Operating System :: Unix',
		'Programming Language :: Python :: 2.7',
		'Topic :: Software Development',
		'Topic :: System :: Monitoring',
		'Topic :: System :: Systems Administration',
	],
)

