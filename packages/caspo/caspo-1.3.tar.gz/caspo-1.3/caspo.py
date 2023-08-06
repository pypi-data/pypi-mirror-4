#!python
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
from __caspo__ import cno, args, utils, Network, Dataset, Learner

if __name__ == '__main__':
    profiler = utils.Profiler()
    arguments = args.get_args()

    print '\nReading input files...'
        
    temp = cno.compress(arguments.pkn, arguments.midas)    
    dataset = Dataset.from_midas(arguments.midas)
    network = Network(temp)

    print 'done.'
    
    learner = Learner(network, dataset)
    profiler.start()
    if arguments.gtts:
        print '\nLearning Boolean logic models and their Global Truth Tables with ASP...',
    else:
        print '\nLearning Boolean logic models with ASP...',

    family = learner.learn(arguments.fit, arguments.size, arguments.discrete, arguments.gtts)
    print 'done in %s sec.' % profiler.stop()
    
    if arguments.gtts:
        print "%s Boolean logic models and %s Global Truth Tables have been learned.\n" % (len(family), len(family.gtts))
    else:
        print "%s Boolean logic models have been learned.\n" % len(family)
    
    writer = utils.Writer(arguments.outdir)
    conjunctions = [str(c) for c in family.conjunctions]

    writer.write(family.to_matrix(), 'models.csv', conjunctions)
    writer.write(family.frequencies, 'frequencies.csv', ['conjunction','frequency'], 
                 lambda r: dict(conjunction=r[0], frequency=r[1]))
                 
    header = ['conjunction_A', 'frequency_A', 'conjunction_B', 'frequency_B']
    writer.write(family.combinatorics('exclusive'), 'exclusive.csv', header)
    writer.write(family.combinatorics('inclusive'), 'inclusive.csv', header)

    if arguments.gtts:    
        gtts_stats = []
        header = dataset.setup.stimuli \
               + map(lambda i: i+'i', dataset.setup.inhibitors) \
               + dataset.setup.readouts
        
        for i,w in enumerate(family.gtts):
            gtts_stats.append(dict(id=i, mse="%.4f" % w.mse(dataset), models=len(w)))
            writer.write(w.to_matrix(dataset.setup), 'gtt-%s.csv' % i, header, verbose=False)

        print "Wrote %s/gtt-%s.csv" % (arguments.outdir, list(range(len(family.gtts))))
        gtts_stats.append(dict(id='family', mse="%.4f" % family.weighted_mse(dataset), models=len(family)))
        writer.write(gtts_stats, 'gtts_stats.csv', ['id', 'mse', 'models'])
        
    if arguments.cross:
        times = arguments.cross[0]
        kfolds = arguments.cross[1]
        
        print '\nRunning %s random %s-fold cross validation... ' % (times, kfolds)
        results = learner.validate(arguments.fit, arguments.size, arguments.discrete, times, kfolds)
        for i,res in enumerate(results):
            writer.write(res, 'cross_validation_%s.csv' % (i+1), ['gtts', 'mse', 'models'])

        print 'done.'

    utils.clean_up()
