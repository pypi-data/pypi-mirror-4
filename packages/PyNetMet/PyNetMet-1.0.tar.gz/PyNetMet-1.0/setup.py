#    Copyright (C) 2012 Daniel Gamermann <daniel.gamermann@ucv.es>
#
#    This file is part of PyNetMet
#
#    PyNetMet is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyNetMet is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyNetMet.  If not, see <http://www.gnu.org/licenses/>.
#
#    
#    Please, cite us in your reasearch!
#


from distutils.core import setup

ld = """This package contains classes defining chemical reaction objects,
 network objects, metabolism objects and FBA objects. These are intended
 to study, analyze and work with metabolic models and their derived networks."""

setup(name = "PyNetMet",
      version = "1.0",
      description = "Tools for analyzing networks and metabolic models.",
      long_description = ld,
      url = "http://pypi.python.org/pypi/PyNetMet",
      author = "Daniel Gamermann",
      author_email = "daniel.gamermann.ucv.es",
      license = "GNU GPLv3",
      package_dir={'PyNetMet' : 'PyNetMet'},
      packages=['PyNetMet'],
      requires = ["PIL","glpk"],
      classifiers=[
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Intended Audience :: Science/Research',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Chemistry',
          'Topic :: Scientific/Engineering :: Mathematics',
          ])

