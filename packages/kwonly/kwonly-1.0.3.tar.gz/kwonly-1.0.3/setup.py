#!/usr/bin/env python

##    Copyright 2012 Garrett Beaty
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

readme = open('README')
try:
    description = readme.readline()
    long_description = ''.join(readme.readlines())
finally:
    readme.close()

classifiers = '''\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python :: 2
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.1
Programming Language :: Python :: 3.2
'''[:-1]

setup(
    name='kwonly',
    version='1.0.3',
    description=description,
    long_description=long_description,
    author='Garrett Beaty',
    author_email='garrett.beaty@gmail.com',
    url='https://code.google.com/p/python-kwonly',
    py_modules=['kwonly'],
    package_dir={'': 'src'},
    requires=['decorator'],
    classifiers=classifiers.split('\n')
    )
