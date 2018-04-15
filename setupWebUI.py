import os
from setuptools import setup


def read(filename):
	return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
	name='GII_0_17.02_SNSI',
	version='0.2.0a0',
	author='Mario Bartolome',
	author_email='mbm0089@alu.ubu.es',
	long_description=read('README.md'),
	packages=['frontend'],
	include_package_data=True,
	install_requires=[
		'flask-login',
		'flask-wtf',
		'flask-sqlalchemy',
		'flask-migrate',
		'flask-socketio',
		'eventlet',
		'flask'
	],
	zip_safe=False
)
