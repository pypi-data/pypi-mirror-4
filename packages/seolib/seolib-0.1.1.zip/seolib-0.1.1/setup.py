# -*- coding: UTF-8 -*-


try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup


requires = ['requests>=1.1.0', 'lxml>=2.3.4']

packages = ['seolib']


setup(
	name='seolib',
	version='0.1.1',
	description='Python lib that provides some usefull and simple methods to obtain website metrics',
	long_description=open('README.rst').read(),
	author='Andrey Bernatsky',
	author_email='xelblch@gmail.com',
	license=open('LICENSE').read(),
	url='http://www.xelblch.com/seolib/',
	download_url='http://www.xelblch.com/seolib/seolib-0.1.1.zip',

	include_package_data=True,
	packages=packages,
	install_requires=requires,

	classifiers=(
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'License :: OSI Approved :: Apache Software License',
		'Intended Audience :: Developers',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX',
		'Operating System :: Unix',
		'Programming Language :: Python',
	    'Programming Language :: Python :: 2.6',
	    'Programming Language :: Python :: 2.7',
	),
)