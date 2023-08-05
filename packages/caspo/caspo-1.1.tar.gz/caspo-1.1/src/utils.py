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
import os
from itertools import chain, combinations

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def hyperedge2str(sources, target):
    neg = ''
    if sources.arg(1) == -1:
        neg = '!'
    
    hn = neg + sources.arg(0)[1:-1]
    next = sources.arg(2)
    
    while next != "end" :
        neg = ''
        if next.arg(1) == -1:
            neg = '!'
        
        hn = hn + "+" + neg + next.arg(0)[1:-1]
        next = next.arg(2)
    
    hn = hn + "=" + target
    return hn

def get_gtt(model, data):

    gtt = []
    for exp in powerset(data.stimulus + data.inhibitors):
        inputs = {}
        gtt_inputs = {}
        for s in data.stimulus:
            inputs[s] = gtt_inputs[s] = False

        for i in exp:
            if i in data.stimulus:
                inputs[i] = gtt_inputs[i] = True
            else:
                inputs[i] = gtt_inputs[i + 'i'] = False

        row = {}
        for readout in data.readouts:
            row[readout] = int(solve_node(readout, inputs, model, data))

        for k,v in gtt_inputs.iteritems():
            row[k] = int(v)
        
        gtt.append(row)

    return gtt

def solve_clause(clause, inputs, clauses, data, visited):
    value = True
    nodes = clause.arg(0)
    while nodes != "end" and value:
        sign = nodes.arg(1)
        if sign == 1:
            value = value and solve_node(nodes.arg(0)[1:-1], inputs, clauses, data, visited)
        else:
            value = value and not solve_node(nodes.arg(0)[1:-1], inputs, clauses, data, visited)
        nodes = nodes.arg(2)
    return value

def solve_node(node, inputs, clauses, data, visited=[]):
    if node in data.stimulus:
        return inputs[node]
    elif node in data.inhibitors and inputs.has_key(node):
        return inputs[node]
    elif node in visited:
        return False
    else:
        or_clauses = [c for c in clauses if c.pred() == "clause" and c.arg(2)[1:-1] == node]
        value = False
        for or_clause in or_clauses:
            value = value or solve_clause(or_clause, inputs, clauses, data, visited + [node])

        return value

def get_mse(model, data):
    rss = 0.
    obs = 0
    for e,o in zip(data.exp_conditions, data.real()):
        inputs = {}
        for inp, value in e.iteritems():
            if inp in data.stimulus:
                inputs[inp] = value == 1
            else:
                if value == 0:
                    inputs[inp] = False

        for readout, value in o.iteritems():
            val = int(solve_node(readout, inputs, model, data))

            rss = rss + pow(value - val, 2)
            obs = obs + 1

    return rss / obs
    
def get_matrix(models, hyperedges):
    matrix = []
    for model in models:
        matrixrow = {}
        m = model.to_list()
        for i in m:
            if i.pred() == "i" :
                matrixrow[hyperedge2str(i.arg(0),i.arg(2)[1:-1])] = 1
    
        ah = [h for h in hyperedges if h not in matrixrow.keys()]
        for h in ah:
            matrixrow[h] = 0
    
        matrix.append(matrixrow)

    return matrix

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
