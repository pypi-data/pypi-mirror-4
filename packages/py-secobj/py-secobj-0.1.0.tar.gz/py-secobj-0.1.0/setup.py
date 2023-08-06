#!/usr/bin/env python

# Copyright (C) 2013  Jay Deiman
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from distutils.core import setup

setup(name='py-secobj' ,
    version='0.1.0' ,
    author='Jay Deiman' ,
    author_email='admin@splitstreams.com' ,
    url='http://stuffivelearned.org/doku.php?id=programming:python:py-secobj' ,
    description='A simple object encryptor and decrytor' ,
    py_modules=['secobj'] ,
    classifiers=[
        'Development Status :: 4 - Beta' ,
        'Intended Audience :: Developers' ,
        'Intended Audience :: System Administrators' ,
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)' ,
        'Operating System :: OS Independent' ,
        'Programming Language :: Python :: 2' ,
        'Topic :: Software Development :: Libraries' ,
        'Topic :: Software Development :: Libraries :: Python Modules' ,
        'Topic :: Utilities' ,
    ]
)
