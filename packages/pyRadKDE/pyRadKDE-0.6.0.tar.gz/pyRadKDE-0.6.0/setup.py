#!/usr/bin/env python
# encoding: utf-8

#    Copyright © 2009 Arne Babenhauserheide
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

"""pyRad setup (install)"""

# We use the advanced setuptools.
#try:
#    from distutils.core import setup
#except ImportError: 
from setuptools import setup
# If we have one or more packages, we also need to import find packages
# It is currently not necessary.
# The corresponding line in setup() is commented out, too.
# from setuptools import find_packages

# Get the docstring of the main module. This will serve as long description.
from pyrad import __doc__ as pyrad__doc__

# Also get version and changelog. Changelog is read from the file Changelog.txt
from pyrad import __version__

def read_changelog():
    """Read and return the Changelog"""
    try:
        f = open("Changelog.txt", "r")
        log = f.read()
        f.close()
    except:
        log = ""
    return log

__changelog__ = read_changelog()


# Create the desription from the docstrings

# The name for PyPI
NAME = pyrad__doc__.split("\n")[0].split(" - ")[0]

# The one line description for PyPI is the part after the dash (" - ") in the first line of this fiels docstring..
DESCRIPTION = pyrad__doc__.split("\n")[0].split(" - ")[1]

# The longer description is built from various sources.

#  The second and following lines of this files doocstring
LONG_DESCRIPTION = "\n".join(pyrad__doc__.split("\n")[1:])

# And the Changelog from Changelog.txt

LONG_DESCRIPTION += "\n\n" + __changelog__


# Fire up setup with these values.i- must be modified.
setup(name=NAME,
      version=__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author='Arne Babenhauserheide',
      author_email='arne_bab@web.de',
      keywords=["babtools"],
      license="GNU GPL-3 or later",
      platforms=["any"],
      requires = ["PyQt4", "PyKDE4"],
      # All classifiers can be found via python setup.py register --list-classifiers
      classifiers = [
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Intended Audience :: End Users/Desktop",
            "Environment :: X11 Applications :: KDE",
            "Development Status :: 4 - Beta"
            ],
      url='http://draketo.de/light/english/pyrad',
      #packages = find_packages('.'),
      data_files = [("share/pyrad", ["images/Wikimedia_Flattr_Button.png"])], 
      py_modules=["rad"],
      scripts=["pyrad.py"]
     )
