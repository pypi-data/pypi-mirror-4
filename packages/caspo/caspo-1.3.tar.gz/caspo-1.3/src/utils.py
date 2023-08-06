# Copyright (c) 2012-2013, Santiago Videla, Sven Thiele, CNRS, INRIA, EMBL
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
import os
import csv

class Profiler(object):
    def __init__(self):
        self.times = None
        
    def start(self):
        self.times = os.times()
        
    def stop(self):
        times = os.times()
        return times[0] - self.times[0] + times[1] - self.times[1]
        
class Writer(object):
    
    def __init__(self, outdir):
        self.outdir = outdir + '/'
        if not os.path.exists(outdir):
            os.mkdir(outdir)

    def write(self, iterable, filename, header=None, rowmaker=lambda r: r, verbose=True):
        f = open(self.outdir + filename, 'w')
        if header:
            writer = csv.DictWriter(f, header)
            writer.writeheader()
        else:
            writer = csv.writer(f)

        for row in iterable:
            writer.writerow(rowmaker(row))

        if verbose:
            print "Wrote %s" % self.outdir + filename
            
        f.close()
                    
def clean_up():
    if os.path.isfile("parser.out"): os.remove("parser.out")
    if os.path.isfile("parsetab.py"): os.remove("parsetab.py")
    if os.path.isfile("parsetab.pyc"): os.remove("parsetab.pyc")
    if os.path.isfile("asp_py_lextab.py"): os.remove("asp_py_lextab.py")
    if os.path.isfile("asp_py_lextab.pyc"): os.remove("asp_py_lextab.pyc")
    if os.path.isfile("asp_py_parsetab.py"): os.remove("asp_py_parsetab.py")
    if os.path.isfile("asp_py_parsetab.pyc"): os.remove("asp_py_parsetab.pyc")
    if os.path.isfile("sif_parser_lextab.py"): os.remove("sif_parser_lextab.py")
    if os.path.isfile("sif_parser_lextab.pyc"): os.remove("sif_parser_lextab.pyc")
