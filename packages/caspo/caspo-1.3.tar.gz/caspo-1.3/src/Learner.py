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
from random import shuffle
from pyasp.asp import GringoClasp, GringoClaspOpt, Term, TermSet

from asp import hyper_prg, functions_prg, optimization_prg, _
from BooleanFamily import BooleanFamily
from Conjunction import Conjunction
from Dataset import Dataset

class Learner(object):
    """
    :param pkn: :class:`__caspo__.Network.Network` instance
    :param dataset: :class:`__caspo__.Dataset.Dataset` instance
    """
    def __init__(self, pkn, dataset):
        self.pkn = pkn
        self.dataset = dataset

    def learn(self, fit_tol, size_tol, discrete, gtts=False, learning=[]):
        """
        Learn logic models
        
        :param fit_tol: fitness tolerance
        :param size_tol: size tolerance
        :param discrete: multi-valued discretization
        :param gtts: compute GTTs
        :param learning: indices to use from the dataset
        :results: :class:`__caspo__.BooleanFamily.BooleanFamily`
        """
        observations = self.dataset.termset(discrete, learning)
        network = self.pkn.termset()
        setup = self.dataset.setup.termset()
        instance = observations.union(setup).union(network)
        
        optimum, model = self.__learn_optimal__(instance)
        
        conjunctions = map(lambda h: Conjunction.from_term(h), filter(lambda t: t.pred() == 'sub', model[0]))
        conjunctions.sort(key=len)
        
        fit = optimum[0]
        size = optimum[1]
        models = self.__learn_suboptimal__(instance, int(fit + fit*fit_tol), size + size_tol)
        
        return BooleanFamily.from_termsets(models, self.dataset.setup, conjunctions, gtts)

    def validate(self, fit_tol, size_tol, discrete, times, kfolds):
        """
        Run k-fold cross validation
        
        :param fit_tol: fitness tolerance
        :param size_tol: size tolerance
        :param discrete: multi-valued discretization
        :param times: cross validation iterations
        :param kfolds: folds for the cross-validation
        :returns: iterator over the results
        """
        for i in xrange(times):
            iresults = []
            folds = self.__k_folds__(range(len(self.dataset)), kfolds)
            
            for k, (learning, testing) in enumerate(folds):
                family = self.learn(fit_tol, size_tol, discrete, True, learning)
                iresults.append(dict(gtts=len(family.gtts), mse=family.weighted_mse(self.dataset, testing), models=len(family)))

            yield iresults
        
    def __k_folds__(self, xs, k):
        shuffle(xs)
        for i in xrange(k):
        	training = [x for j, x in enumerate(xs) if j % k != i]
        	validation = [x for j, x in enumerate(xs) if j % k == i]
        	yield training, validation

    def __learn_optimal__(self, instance):
        prg = [instance.to_file(), hyper_prg, functions_prg, optimization_prg]
        coptions='--heu=Vsids --opt-hier=2 --opt-heu=2'
        solver = GringoClaspOpt(clasp_options=coptions)
        addText = "#hide. #show conjunction/3. #show sub/3."
        optimum = solver.run(prg, collapseTerms=False, collapseAtoms=False, additionalProgramText=addText)
        os.unlink(prg[0])
        return optimum

    def __learn_suboptimal__(self, instance, fit, size):
        prg = [instance.to_file(), hyper_prg,functions_prg]
        goptions='--const maxresidual=%s --const maxsize=%s' % (fit, size)
        coptions='--heu=Vsids'
        solver = GringoClasp(gringo_options=goptions,clasp_options=coptions)
        addText = "#hide. #show conjunction/3."
        answers = solver.run(prg, nmodels=0, collapseTerms=False, collapseAtoms=False, additionalProgramText=addText)
        os.unlink(prg[0])
        return answers
