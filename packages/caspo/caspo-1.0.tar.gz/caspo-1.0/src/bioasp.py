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
from __future__ import absolute_import
import os
from __caspo__ import cno, utils
from bioasp.data import psn
from bioasp.query import psnoptimization as pno
from bioasp.asp import GringoClasp, Term, TermSet

root = __file__.rsplit('/', 1)[0]

gtt_prg     =   root + '/query/gtt.lp'
mutual_prg  =   root + '/query/mutual.lp'

def get_hyperedges(instance):
	hg = pno.get_hypergraph(instance)
	hyperedges = [utils.hyperedge2str(a, a.arg(4)[1:-1]) for a in hg if a.pred() == "subset"]
	hyperedges.sort(key=len)
	
	return hyperedges


def get_mutual_hyperedges(models):
    solver = GringoClasp()
    nmodels = len(models)
    imodels = TermSet()
    imodels.add(Term('nmodels', [nmodels]))
    for i, model in enumerate(models):
        clauses = filter(lambda t: t.pred() == "clause", model)
        for c in clauses:
            imodels.add(Term('clause',[i+1] + c.arguments))

    mutuals = solver.run([ imodels.to_file(), mutual_prg ], nmodels=1, collapseTerms=False, collapseAtoms=False)
    
    exclusives = []
    inclusives = []
    for mutual in mutuals[0]:
        a = mutual.arg(0)
        b = mutual.arg(1)
        ha = utils.hyperedge2str(a.arg(0), a.arg(2)[1:-1])
        freq_a = a.arg(3) / float(nmodels)
        hb = utils.hyperedge2str(b.arg(0), b.arg(2)[1:-1])
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
            m1 = [c for c in models[i] if c.pred() == "clause"]
            for j in range(i+1,nmodels):
                if eq[j] == -1:
                    m2 = [c for c in models[j] if c.pred() == "clause"]
                    
                    eq_models = TermSet()
                    for c in m1:
                        eq_models.add(Term('clause',[1] + c.arguments))
    
                    for c in m2:
                        eq_models.add(Term('clause',[2] + c.arguments))

                    gtt_instance = instance.union(eq_models)
                    sat = solver.run([ gtt_instance.to_file(), gtt_prg, pno.hyper_prg ], nmodels=1, collapseTerms=False, collapseAtoms=False)
                    if len(sat) == 0:
                        eq[j] = i
    return eq
    
def optimize(pkn, midas, tolerance, pvalue, qvalue):
    print '\nReading observations',midas, '...',
    data = psn.MIDASReader(midas)
    obs = data.getTermSet(factor=pow(10,pvalue))
    print 'done.'

    print '\nReading and compressing network',pkn, '... \n\n',
    temp = "compressed_model.sif"
    cno.compress(pkn, midas, temp)
    net = psn.readSIF(temp)
    os.remove(temp)

    print '\nCreate instance...'
    instance = net.union(obs)

    print '\nComputing score of the optimal BooleanModel...',
    optimum = pno.get_minimal_model_size(instance, pvalue, qvalue)
    print 'done.'    
    print '   The optimal model score is', optimum[0][0],'.' 

    #count clause atoms to determine minimal size
    optsize = 0
    for a in optimum[1][0] :
        if a.pred() == "clause":
            optsize = optsize + int(a.arg(1))
    print '   The optimal size is', optsize,'.'    

    score = int(optimum[0][0] + optimum[0][0]*tolerance)

    print '\nComputing all models with score', score,'and size lower than', optsize,'...',
    models = pno.get_suboptimal_models(instance, score, optsize, pvalue, qvalue)
    print 'done.'

    return models, score, optsize, data, instance
