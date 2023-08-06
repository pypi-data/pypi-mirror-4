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
from pyasp.asp import GringoClasp, TermSet, Term

from asp import gtt_prg, mutual_prg
from BooleanModel import BooleanModel, GTT
from Conjunction import Conjunction

class BooleanFamily(set):
    """
    :param setup: :class:`__caspo__.Dataset.Setup` instance
    :param conjunctions: list of all possible :class:`__caspo__.Conjunction` among the family
    :param gtts: True to compute GTTs, False otherwise.
    
    >>> from __caspo__ import Conjunction, BooleanFamily, Setup
    >>> setup = Setup(['TNFa'], ['p38'], ['Hsp27', 'p38'])
    >>> cs = [Conjunction.from_str('TNFa=Hsp27'), Conjunction.from_str('TNFa=p38')]
    >>> family = BooleanFamily(setup, cs, False)
    >>> len(family)
    0
    """
    def __init__(self, setup, conjunctions, gtts):
        super(BooleanFamily, self).__init__()
        
        self.setup = setup
        self.conjunctions = conjunctions
        self.gtts = None
        if gtts:
            self.gtts = set()
        
        self.occurrences = dict(map(lambda c: (str(c), 0.), self.conjunctions))
        self.__combinatorics = None

    def add(self, model):
        """
        Adds a Boolean model to the family. Updates conjunction's occurrences and GTTs.
        If the model has the input-output behavior of some previously added model, it's added to the corresponding GTT.
        Otherwise, a new GTT is created with this model.
        
        :param model: :class:`__caspo__.BooleanModel` instance to add
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel
        >>> setup = Setup(['TNFa'], ['p38'], ['Hsp27', 'p38'])
        >>> c1 = Conjunction.from_str('TNFa=Hsp27')
        >>> c2 = Conjunction.from_str('TNFa=ras')
        >>> c3 = Conjunction.from_str('ras=Hsp27')
        >>> c4 = Conjunction.from_str('TNFa=p38')
        >>> cs = [c1, c2, c3, c4]
        >>> family = BooleanFamily(setup, cs, True)
        >>> len(family)
        0
        >>> len(family.gtts)
        0
        
        First, we add a model having only `c1` and since the family is empty, a new GTT is created.
        
        >>> family.add(BooleanModel([c1]))
        >>> len(family)
        1
        >>> len(family.gtts)
        1
        
        Next, we add a model having `c2` and `c3` which is equivalent to the previous model.
        
        >>> family.add(BooleanModel([c2,c3]))
        >>> len(family)
        2
        >>> len(family.gtts)
        1
        
        Finally, if we add a model having a different input-output behavior, a new GTT is created.
        
        >>> family.add(BooleanModel([c4]))
        >>> len(family)
        3
        >>> len(family.gtts)
        2
        
        Now, let's check the GTTs and their corresponding gathered models. Note that we convert 
        `family.gtts` into a list only for testing (sets don't preserve any order), but you don't 
        need to do it in your code.
        
        >>> for gtt in sorted(family.gtts):
        ...     print gtt.vector(), [m.vector() for m in gtt.models]
        {'TNFa=Hsp27': 1} [{'TNFa=ras': 1, 'ras=Hsp27': 1}]
        {'TNFa=p38': 1} []
        """
        super(BooleanFamily, self).add(model)
        
        for h in model.vector():
            self.occurrences[h] += 1

        if self.gtts != None:
            self.__update_gtts__(model)
                
    @property
    def frequencies(self):
        """
        Returns an iterator over tuples (h,f) where `h` is the string representation of a conjunction 
        and `f` its frequency in the family.
        
        :returns: iterator
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel
        >>> setup = Setup(['TNFa'], ['p38'], ['Hsp27', 'p38'])
        >>> c1 = Conjunction.from_str('TNFa=Hsp27')
        >>> c2 = Conjunction.from_str('TNFa=ras')
        >>> c3 = Conjunction.from_str('ras=Hsp27')
        >>> c4 = Conjunction.from_str('TNFa=p38')
        >>> c5 = Conjunction.from_str('ras=p38')
        >>> cs = [c1, c2, c3, c4, c5]
        >>> family = BooleanFamily(setup, cs, False)
        >>> family.add(BooleanModel([c1]))
        >>> family.add(BooleanModel([c2,c3]))
        >>> family.add(BooleanModel([c4]))
        >>> family.add(BooleanModel([c2,c5]))
        >>> print list(family.frequencies)
        [('TNFa=Hsp27', 0.25), ('TNFa=ras', 0.5), ('ras=p38', 0.25), ('ras=Hsp27', 0.25), ('TNFa=p38', 0.25)]
        """
        nmodels = len(self)
        for h,o in self.occurrences.iteritems():
            yield h, o / nmodels

    def combinatorics(self, mode, update=False):
        """
        Returns an iterator over the mutual inclusive/exclusive conjunctions.
        
        :param mode: either 'exclusive' or 'inclusive'
        :param update: True to force to re-compute combinatorics.
        :returns: iterator
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel
        >>> setup = Setup(['TNFa'], ['p38'], ['Hsp27', 'p38'])
        >>> c1 = Conjunction.from_str('TNFa=Hsp27')
        >>> c2 = Conjunction.from_str('TNFa=ras')
        >>> c3 = Conjunction.from_str('ras=Hsp27')
        >>> cs = [c1, c2, c3]
        >>> family = BooleanFamily(setup, cs, False)
        >>> family.add(BooleanModel([c1]))
        >>> family.add(BooleanModel([c2,c3]))
        >>> for m in family.combinatorics('exclusive'):
        ...     print m['conjunction_A'], m['frequency_A'], m['conjunction_B'], m['frequency_B']
        TNFa=Hsp27 0.5 TNFa=ras 0.5
        TNFa=Hsp27 0.5 ras=Hsp27 0.5
        
        >>> for m in family.combinatorics('inclusive'):
        ...     print m['conjunction_A'], m['frequency_A'], m['conjunction_B'], m['frequency_B']
        ras=Hsp27 0.5 TNFa=ras 0.5
        """
        if not self.__combinatorics or update:
            self.__combinatorics = self.__mutuals__()
        
        nmodels = float(len(self))
        for mutual in self.__combinatorics:
            if mutual.pred() == mode:
                ta = mutual.arg(0)
                tb = mutual.arg(1)
            
                m = dict(conjunction_A=Conjunction.from_term(ta), frequency_A=ta.arg(3) / nmodels, 
                        conjunction_B=Conjunction.from_term(tb), frequency_B=tb.arg(3) / nmodels)
                     
                yield m

    @classmethod
    def from_termsets(cls, termsets, setup, conjunctions, gtts):
        """
        Constructor from a list of PyASP TermSet instances.
        
        :param termsets: list of TermSet
        :param setup: :class:`__caspo__.Dataset.Setup` instance
        :param conjunctions: list of all possible :class:`__caspo__.Conjunction` among the family
        :param gtts: True to compute GTTs, False otherwise.
        :returns: :class:`__caspo__.BooleanFamily`
        """
        family = cls(setup, conjunctions, gtts)
        for t in termsets:
            family.add(BooleanModel.from_termset(t))

        return family

    @classmethod
    def from_matrix(cls, matrix, setup, conjunctions, gtts):
        """
        Constructor from a matrix representation of logic models
        
        :param matrix: iterator over rows in the matrix. Each row describes a model
        :param setup: :class:`__caspo__.Setup` instance
        :param conjunctions: list of all possible :class:`__caspo__.Conjunction` among the family
        :param gtts: True to compute GTTs, False otherwise.
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup
        >>> setup = Setup(['TNFa'], ['p38'], ['Hsp27', 'p38'])
        >>> cs = [Conjunction.from_str('TNFa=Hsp27'), Conjunction.from_str('TNFa=p38')]
        >>> matrix = [{'TNFa=Hsp27': '1', 'TNFa=p38': '0'}, {'TNFa=Hsp27': '0', 'TNFa=p38': '1'}]
        >>> family = BooleanFamily.from_matrix(matrix, setup, cs, False)
        >>> len(family)
        2
        >>> print list(family.frequencies)
        [('TNFa=Hsp27', 0.5), ('TNFa=p38', 0.5)]
        """
        family = cls(setup, conjunctions, gtts)
        for v in matrix:
            family.add(BooleanModel.from_vector(v))

        return family
        
    def weighted_mse(self, dataset, testing=[]):
        """
        Compute the weighted MSE of the family. If GTTs were computed, each output prediction is weighted
        according to the number of models gathered by the corresponding GTT. Otherwise, output predictions
        are summed over all models in the family. If the family is complete, both computation are equivalent.
        
        :param dataset: :class:`__caspo__.Dataset` instance
        :param testing: list of experiment indices
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel
        >>> setup = Setup(['TNFa'], ['p38'], ['Hsp27', 'p38'])
        >>> c1 = Conjunction.from_str('TNFa=Hsp27')
        >>> c2 = Conjunction.from_str('TNFa=ras')
        >>> c3 = Conjunction.from_str('ras=Hsp27')
        >>> c4 = Conjunction.from_str('TNFa=p38')
        >>> cs = [c1, c2, c3, c4]
        >>> family = BooleanFamily(setup, cs, True)
        >>> family.add(BooleanModel([c1]))
        >>> family.add(BooleanModel([c2,c3]))
        >>> family.add(BooleanModel([c4]))
        
        Now, let's create a fake dataset and compute the family's MSE
        
        >>> from __caspo__ import Dataset, Experiment, Conjunction
        >>> e0 = Experiment({'TNFa': 1, 'p38': 0}, {10: {'Hsp27':0.8, 'p38': 0}})
        >>> e1 = Experiment({'TNFa': 0, 'p38': 1}, {10: {'Hsp27':0.2, 'p38':0}})
        >>> dataset = Dataset([e0, e1], ['TNFa'], ['p38'], ['Hsp27', 'p38'], 10)
        >>> print "%.4f" % family.weighted_mse(dataset) # ((2/3 - 0.8)^2 + (0 - 0.2)^2) / 4
        0.0144
        """
        rss = 0.
        obs = 0
        total = float(len(self))
        
        if len(testing) == 0:
            testing = xrange(len(dataset))
        
        for exp in (dataset[i] for i in testing):
            inputs = exp.boolean_input(dataset.setup)
            outputs = exp.outputs[dataset.time_point]
            
            for readout, value in outputs.iteritems():
                val = 0
                if self.gtts != None:
                    for gtt in self.gtts:
                        val = val + int(gtt.resolve(readout, inputs, dataset.setup)) * len(gtt)
                else:
                    for model in self:
                        val = val + int(model.resolve(readout, inputs, dataset.setup))

                rss = rss + pow(value - val / total, 2)
                obs = obs + 1

        return rss / obs    
                        
    def to_matrix(self):
        """
        Returns an iterator over all models in the family as vectors (key-value: conjunction-{0,1})
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel
        >>> setup = Setup(['TNFa'], ['p38'], ['Hsp27', 'p38'])
        >>> c1 = Conjunction.from_str('TNFa=Hsp27')
        >>> c2 = Conjunction.from_str('TNFa=ras')
        >>> c3 = Conjunction.from_str('ras=Hsp27')
        >>> c4 = Conjunction.from_str('TNFa=p38')
        >>> cs = [c1, c2, c3, c4]
        >>> family = BooleanFamily(setup, cs, True)
        >>> family.add(BooleanModel([c1]))
        >>> family.add(BooleanModel([c2,c3]))
        >>> family.add(BooleanModel([c2,c3,c4]))
        >>> for model in sorted(family.to_matrix(), key=lambda v: v.values().count(1)):
        ...     print model
        {'TNFa=Hsp27': 1, 'TNFa=ras': 0, 'ras=Hsp27': 0, 'TNFa=p38': 0}
        {'TNFa=Hsp27': 0, 'TNFa=ras': 1, 'ras=Hsp27': 1, 'TNFa=p38': 0}
        {'TNFa=Hsp27': 0, 'TNFa=ras': 1, 'ras=Hsp27': 1, 'TNFa=p38': 1}
        """
        vector = {}
        
        vector = dict(map(lambda c: (str(c), 0), self.conjunctions))
        for model in self:
            v = vector.copy()
            v = model.vector(v)
            yield v

    def __update_gtts__(self, model):
        if len(self.gtts) > 0:
            solver = GringoClasp()
    
            setup = self.setup.termset()
            m1 = model.termset(1)
            inst = setup.union(m1)
            
            added = False
            for gtt in self.gtts:
                m2 = gtt.termset(2)
                instance = inst.union(m2)
                prg = [instance.to_file(), gtt_prg]
                sat = solver.run(prg, nmodels=1, 
                                 collapseTerms=False, collapseAtoms=False)
                                 
                os.unlink(prg[0])
                if len(sat) == 0:
                    gtt.add(model)
                    added = True
                    break
                    
            if not added:
                self.gtts.add(GTT(model))
        else:
            self.gtts.add(GTT(model))
        
    def __mutuals__(self):
        solver = GringoClasp()
        nmodels = len(self)
        
        instance = TermSet()
        instance.add(Term('nmodels', [nmodels]))
        
        for i, model in enumerate(self):
            instance = instance.union(model.termset(i+1))

        prg = [instance.to_file(), mutual_prg]
        mutuals = solver.run(prg, nmodels=1, 
                             collapseTerms=False, collapseAtoms=False)

        os.unlink(prg[0])
        return mutuals[0]
