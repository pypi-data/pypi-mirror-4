#! python
# -*- coding: utf-8 -*-
'''
    PyResizeImage: Resize images, and pad them to give an exact size image
    Copyright (C) 2013  Alkatron, (alkatron@gmail.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
#from distutils.core import setup
from setuptools import setup, find_packages
from pyrszimg import VVERSION, read

setup(
    name = "PyResizeImage",
    version = VVERSION,
    include_package_data = True,
    packages=find_packages(),
    #package_data={'':['COPYING.txt', 'README.txt']},
    scripts=['pyresizeimage'],
    description = "Resize images, and pad them to give an exact size image",
    author = "Alkatron",
    author_email = "alkatron@gmail.com",
    url = "https://launchpad.net/pyresizeimage",
    keywords = ["graphic", "image", "png","jpg","aspect ratio"],
    install_requires=['PIL',],
    license='GPLv3',
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
        ],
    long_description = '\n\n\n\n\n\n%s' %(read('README.txt')),
)

