#!/usr/bin/python
"""
Copyright 2013 Brian Mearns

This file is part of Tome.

Tome is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Tome is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Tome.  If not, see <http://www.gnu.org/licenses/>.
"""
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import sys
import os
import cStringIO


### This is a lot of screwing around to populate the README for the package from
# a template we have in the templ directory.
sys.path.insert(0, "src/tome")
import version

lid = open("LICENSE.txt", "r")
license = lid.read()
lid.close()

rid = open("README.txt", "r")
readme = rid.read()
rid.close()

setup(
    name='tome',
    version=version.setuptools_string(),
    author='Brian Mearns',
    author_email='bmearns@ieee.org',
    url='https://bitbucket.org/bmearns/tome/',
    license=license,
    description='Tome Markup Language for authors.',
    long_description=readme,

    install_requires=["templ>=1.0"],

    package_dir={'': 'src'},
    packages=find_packages('src'),  #Looks for __init__.py
    include_package_data = True,    #Uses MANIFEST.in
    data_files = [
        ('misc', ['LICENSE.txt', 'README.txt', 'TODO.txt', 'BUGS.txt', 'CHANGES.txt']),
    ],


    entry_points = {
        "console_scripts" : [
            'tome = tome.main:main',
            'tome-epub-template = tome.main:writeEpubTemplate',
            'tome-latex-template = tome.main:writeLatexTemplate',
            'tome-xml-schema = tome.main:writeXmlSchema',
        ],
    }
)

