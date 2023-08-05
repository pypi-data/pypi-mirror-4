# Copyright (c) 2012, Sven Thiele <sthiele78@gmail.com>
#
# This file is part of caspo.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caspo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-
from setuptools import setup
import os
import sys
import platform
import distutils
import site
import sysconfig
import urllib

from setuptools.command.install import install as _install

CNO_URL = "http://www.bioconductor.org/packages/2.12/bioc/src/contrib/CellNOptR_1.5.0.tar.gz"
CNO_FILE = "CNO.tar.gz"

class install(_install):
    def run(self):
        _install.run(self)
        # download and install CellNOptR
        urllib.urlretrieve(CNO_URL, CNO_FILE)
        code = os.system("R CMD INSTALL %s" % CNO_FILE)
        os.remove(CNO_FILE)
        
        if code != 0:
            print "\nThere was an error trying to install CellNOptR. Please install it manually before using caspo.\n"
                         
setup(cmdclass={'install': install},
      name='caspo',
      version='1.0',
      url='http://pypi.python.org/pypi/caspo/',
      license='LICENSE.txt',
      description='Learning of Protein Signaling Logic Models powered by BioASP and CellNOptR',
      long_description=open('README.txt').read(),
      author='Sven Thiele, Santiago Videla',
      author_email='sthiele@irisa.fr, santiago.videla@irisa.fr',
      packages = ['__caspo__'],
      package_dir = {'__caspo__' : 'src'},
      package_data = {'__caspo__' : ['query/*.lp']},
      scripts = ['caspo.py'],
      install_requires=[
        "cellnopt.wrapper",
        "bioasp"
      ]
)