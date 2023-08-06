# from distutils.core import setup
from setuptools import setup

setup(
	name='redact',
	url='https://github.com/zweifisch/redact',
	version='0.0.3',
	description='rendering config files from templates',
	author='Feng Zhou',
	author_email='zf.pascal@gmail.com',
	packages=['redact'],
	install_requires=['PyYAML','opster'],
	entry_points={
		'console_scripts': ['redact=redact:redact'],
   },
)
