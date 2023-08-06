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
from __future__ import absolute_import
import os
from __caspo__ import cno, utils, data
from pyasp.asp import GringoClasp, GringoClaspOpt, Term, TermSet

#hook to remove "" from terms arguments
Term._arg = lambda s,n: s.arg(n)[1:-1]

root = __file__.rsplit('/', 1)[0]

functions_prg       =  root + '/query/functions.lp'
hyper_prg           =  root + '/query/hyper.lp'
optimization_prg    =  root + '/query/optimization.lp'
gtt_prg             =  root + '/query/gtt.lp'
mutual_prg          =  root + '/query/mutual.lp'

def optimize(pkn, midas, tolerance, pvalue):
    print '\nReading observations',midas, '...',
    dataset = data.MIDASReader(midas)
    obs = dataset.getTermSet(factor=pow(10,pvalue))
    print 'done.'

    print '\nReading and compressing network',pkn, '... \n\n',
    temp = "compressed_model.sif"
    cno.compress(pkn, midas, temp)
    net = data.readSIF(temp)
    os.remove(temp)

    print '\nCreate instance...'
    instance = net.union(obs)
    
    print '\nSearching one global optimal model...',
    optimum, model = get_optimal_model(instance, pvalue)
    print 'done.'    
    
    optsize = optimum[1]
    print 'The optimal model size is %s.' % optsize

    score = int(optimum[0] + optimum[0]*tolerance)

    print 'Enumerating all models using tolerance %s and size lower than %s... ' % (tolerance,optsize),
    models = get_suboptimal_models(instance, score, optsize, pvalue)
    print 'done.'
    
    return models, score, optsize, dataset, instance


def get_mutual_hyperedges(models):
    solver = GringoClasp()
    nmodels = len(models)
    imodels = TermSet()
    imodels.add(Term('nmodels', [nmodels]))
    for i, model in enumerate(models):
        for c in model:
            imodels.add(Term('conjunction',[i+1] + c.arguments))

    mutuals = solver.run([imodels.to_file(), mutual_prg], nmodels=1, collapseTerms=False, collapseAtoms=False)
    
    exclusives = []
    inclusives = []
    for mutual in mutuals[0]:
        a = mutual.arg(0)
        b = mutual.arg(1)
        ha = utils.hyperedge2str(a.arg(0), a._arg(2))
        freq_a = a.arg(3) / float(nmodels)
        hb = utils.hyperedge2str(b.arg(0), b._arg(2))
        freq_b = b.arg(3) / float(nmodels)
        if mutual.pred() == "exclusive":
            exclusives.append((ha,freq_a,hb,freq_b))
        else:
            inclusives.append((ha,freq_a,hb,freq_b))
            
    return exclusives, inclusives
	
def get_models_equivalences(models, instance):   
    solver = GringoClasp()
    nmodels = len(models)
    eq = [-1] * nmodels
    
    for i in range(0,nmodels):
        if eq[i] == -1:
            eq[i] = i
            for j in range(i+1,nmodels):
                if eq[j] == -1:
                    eq_models = TermSet()
                    for c in models[i]:
                        eq_models.add(Term('conjunction',[1] + c.arguments))
    
                    for c in models[j]:
                        eq_models.add(Term('conjunction',[2] + c.arguments))

                    gtt_instance = instance.union(eq_models)
                    sat = solver.run([gtt_instance.to_file(), gtt_prg, hyper_prg], nmodels=1, collapseTerms=False, collapseAtoms=False)
                    if len(sat) == 0:
                        eq[j] = i
    return eq



def get_optimal_model(instance, p):
    prg = [ instance.to_file(), hyper_prg,functions_prg,optimization_prg]
    goptions='--const p=%s' % p
    coptions='--opt-hier=2'
    solver = GringoClaspOpt(gringo_options=goptions,clasp_options=coptions)
    optimum = solver.run(prg, collapseAtoms=False,additionalProgramText="#hide. #show conjunction/3.")
    os.unlink(prg[0])
    return optimum

def get_suboptimal_models(instance, score, size, p):
    prg = [ instance.to_file(), hyper_prg,functions_prg,optimization_prg]
    goptions='--const p=%s --const maxsize=%s' % (p,str(size))
    coptions='--opt-hier=2 --opt-all='+str(score)
    solver = GringoClasp(gringo_options=goptions,clasp_options=coptions)
    answers = solver.run(prg, nmodels=0, collapseTerms=False, collapseAtoms=False, additionalProgramText="#hide. #show conjunction/3.")
    os.unlink(prg[0])
    return answers 

def get_hyperedges(instance):
    prg = [instance.to_file(), hyper_prg]   
    options=''
    solver = GringoClasp(clasp_options=options)
    hg = solver.run(prg, collapseTerms=False, collapseAtoms=False, additionalProgramText="#hide. #show sub/3.")

    hyperedges = [utils.hyperedge2str(a.arg(0), a._arg(2)) for a in hg[0]]
    hyperedges.sort(key=len)

    return hyperedges
