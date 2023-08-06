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

from pyasp.asp import Term

#hooks to include/remove "" from terms arguments
Term._arg = lambda s,n: s.arg(n)[1:-1]
_ = lambda s: '"' + s + '"'
 
root = __file__.rsplit('/', 1)[0]

functions_prg       =  root + '/query/functions.lp'
hyper_prg           =  root + '/query/hyper.lp'
optimization_prg    =  root + '/query/optimization.lp'
gtt_prg             =  root + '/query/gtt.lp'
mutual_prg          =  root + '/query/mutual.lp'
