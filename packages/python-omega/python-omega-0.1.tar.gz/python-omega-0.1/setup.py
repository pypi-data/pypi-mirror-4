#!/usr/bin/python
from distutils.core import setup

setup(
    name='python-omega',
    version='0.1',
    packages=['omega', 'omega.test'],
	description='The Omega parsing framework',
	author='Timothy Allen',
	author_email='thristian@gmail.com',
	url='https://gitorious.org/python-omega',
	classifiers=[
		"Development Status :: 2 - Pre-Alpha",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Code Generators",
		"Topic :: Software Development :: Compilers",
		"Topic :: Text Processing",
	]
)

