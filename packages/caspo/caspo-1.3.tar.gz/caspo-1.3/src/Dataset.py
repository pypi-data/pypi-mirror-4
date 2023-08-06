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
import csv, math
from itertools import chain, combinations

from pyasp.asp import Term, TermSet

from asp import _

class Experiment(object):
    """
    :param inputs: key-value mapping describing an experimental condition
    :param outputs: key-value mapping describing experimental observations for each time-point    
    """
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        
    def discrete_output(self, time, factor):
        """
        Returns a key-value mapping of discrete observations
        
        :param time: time-point
        :param factor: discretization factor
        :returns: dict
        
        >>> from __caspo__ import Experiment
        >>> e = Experiment({'TNFa': 1, 'TGFa': 0}, {10: {'Hsp27': 0.2, 'CREB': 0.953}})
        >>> e.discrete_output(10, 100)
        {'Hsp27': 20, 'CREB': 95}
        """
        discrete = {}
        for node, value in self.outputs[time].iteritems():
            discrete[node] = int(value * factor)
            
        return discrete
        
    def boolean_input(self, setup):
        """
        Return boolean inputs
        
        >>> from __caspo__ import Setup, Experiment
        >>> setup = Setup(['TNFa', 'TGFa'], [], ['Hsp27', 'CREB'])
        >>> e = Experiment({'TNFa': 1, 'TGFa': 0}, {10: {'Hsp27': 0.2, 'CREB': 0.9}})
        >>> e.boolean_input(setup)
        {'TGFa': False, 'TNFa': True}
        """
        bool_input = {}
        for i, value in self.inputs.iteritems():
            if i in setup.stimuli:
                bool_input[i] = value == 1
            else:
                if value == 0:
                    bool_input[i] = False
        
        return bool_input

class Setup(object):
    """
    :param stimuli: list of stimuli
    :param inhibitors: list of inhibitors
    :param readouts: list of readouts
    """
    def __init__(self, stimuli, inhibitors, readouts):
        self.stimuli = stimuli
        self.inhibitors = inhibitors
        self.readouts = readouts
        
    def termset(self):
        """
        Returns TermSet respresentation
        
        :returns: TermSet
        
        >>> from __caspo__ import Setup
        >>> setup = Setup(['TNFa', 'TGFa'], [], ['Hsp27', 'CREB'])
        >>> setup.termset()
        TermSet([Term('stimulus',['"TGFa"']), Term('readout',['"CREB"']), Term('stimulus',['"TNFa"']), Term('readout',['"Hsp27"'])])
        """
        t = TermSet()
        for s in self.stimuli:
            t.add(Term('stimulus', [_(s)]))
            
        for i in self.inhibitors:
            t.add(Term('inhibitor', [_(i)]))
            
        for r in self.readouts:
            t.add(Term('readout', [_(r)]))
            
        return t
        
    def powerset(self):
        """
        Iterator over all possible experimental conditions
        
        :returns: iterator
        """
        s = list(self.stimuli + self.inhibitors)
        return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

class Dataset(list):
    """
    :param experiments: list of :class:`__caspo__.Dataset.Experiment` instances
    :param stimuli: list of stimuli
    :param inhibitors: list of inhibitors
    :param readouts: list of readouts
    :param time_point: default time-point
    """
    def __init__(self, experiments, stimuli, inhibitors, readouts, time_point):
        super(Dataset, self).__init__(experiments)
        
        self.setup = Setup(stimuli, inhibitors, readouts)
        self.time_point = time_point

    @classmethod
    def from_midas(cls, filepath):
        """
        Constructor from MIDAS file
        
        :param filepath: MIDAS filepath
        :returns: :class:`__caspo__.Dataset.Dataset`
        """
        f = open(filepath, 'rbU')
        reader = csv.DictReader(f)

        #Header without the CellLine column
        species = reader.fieldnames[1:]

        stimuli = map(lambda name: name[3:], filter(lambda name: name.startswith('TR:') and not name.endswith('i'), species))
        inhibitors = map(lambda name: name[3:-1], filter(lambda name: name.startswith('TR:') and name.endswith('i'), species))
        readouts = map(lambda name: name[3:], filter(lambda name: name.startswith('DV:'), species))

        exp_conditions = []
        exp_observations = []
        time_points = []
        for row in reader:
            cond = {}
            for s in stimuli:
                cond[s] = int(row['TR:' + s] or 0)
            for i in inhibitors:
                #In MIDAS, inhibitors are set to 1 when the inhibitor is present meaning that the node it's inhibited
                cond[i] = (int(row['TR:' + i + 'i'] or 0) + 1) % 2

            obs = {}
            for r in readouts:
                #Ignore NaN values
                if not math.isnan(float(row['DV:' + r])):
                    t = int(row['DA:' + r])
                    if not obs.has_key(t):
                        if t not in time_points:
                            time_points.append(t)
                        obs[t] = {}

                    obs[t][r] = float(row['DV:' + r])

            if cond in exp_conditions:
                index = exp_conditions.index(cond)
                exp_observations[index].update(obs)
            else:
                exp_conditions.append(cond)
                exp_observations.append(obs)

        time_points.sort()
        if len(time_points) == 1:
            time_point = time_points[0]
        else:
            time_point = time_points[1]
    
        experiments = []
        for i,o in zip(exp_conditions, exp_observations):
            experiments.append(Experiment(i,o))
    
        return cls(experiments, stimuli, inhibitors, readouts, time_point)

    def termset(self, factor=100, indices=[]):
        """
        Returns TermSet representation
        
        :param factor: discretization factor
        :param indices: list of indices to include in the termset
        :returns: TermSet
        """
        lpfacts = TermSet()
        if len(indices) == 0:
            indices = xrange(len(self))
            
        for index, exp in enumerate((self[i] for i in indices)):
            for name, value in exp.inputs.iteritems():
                lpfacts.add(Term('exp', [index + 1, _(name), value]))
    
            for name, value in exp.discrete_output(self.time_point, factor).iteritems():
                lpfacts.add(Term('obs', [index + 1, _(name), value]))
                
        lpfacts.add(Term('dfactor', [factor]))
        
        return lpfacts