#!/usr/bin/python

from setuptools import setup, find_packages
from multicast import __version__

setup(
	name='multicast',
	version=__version__,
	py_modules=['multicast', 'mnc'],
	author='Iain Lowe',
	author_email='iain.lowe@gmail.com',
	description='Asynchronous multicast UDP for clients and servers',
	license='MIT',
	url='https://bitbucket.org/ilowe/multicast',
	test_suite='nose.collector',
	keywords='io asyncore multicast UDP socket server asynchronous async epoll select',
	entry_points={
		'console_scripts': ['mnc = mnc.argmain']
	}
)
