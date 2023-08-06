# Copyright (c) 2012-2013, Santiago Videla, Sven Thiele, CNRS, INRIA, EMBL
#
# This file is part of caspo.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BioASP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BioASP.  If not, see <http://www.gnu.org/licenses/>.import random

# -*- coding: utf-8 -*-
from pyasp.asp import TermSet, Term
from asp import _

class Network(object):
    """
    :param sif_file: SIF filepath
    """
    def __init__(self, sif_file):
        self.nodes = set()
        self.edges = set()
        
        with open(sif_file, 'rbU') as f:
            for line in f:
                line.replace('\r\n','\n')
                source, sign, target = line[:-1].split('\t')
                self.nodes.add(source)
                self.nodes.add(target)
                self.edges.add((source,target,sign))

    def termset(self):
        """
        Returns TermSet
        
        :returns: TermSet
        """
        network = TermSet()
        for node in self.nodes:
            network.add(Term('vertex', [_(node)]))
            
        for source, target, sign in self.edges:
            network.add(Term('edge', [_(source), _(target), sign]))
    
        return network