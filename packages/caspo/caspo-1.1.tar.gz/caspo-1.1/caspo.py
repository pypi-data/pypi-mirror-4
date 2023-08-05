#!python
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
from optparse import OptionParser
from __caspo__ import bioasp, utils, writer

if __name__ == '__main__':
    usage = "usage: %prog [options] pkn.sif midas.csv" 
    parser = OptionParser(usage)
    parser.add_option("-t", "--tolerance", dest="tolerance", type='float', default=0.,
                      help="Suboptimal enumeration tolerance: 0 <= t <= 0.5 (Default to 0)", metavar="T")

    parser.add_option("-p", "--discrete", dest="pvalue", type="int", default=2,
                      help="Discretization range exponent: 10^P (Default to 2)", metavar="P")
                      
    parser.add_option("-q", "--alpha", dest="qvalue", type="int", default=5,
                    help="Size penalty exponent 1/10^Q (Default to 5)", metavar="Q")
                    
    parser.add_option("-g", "--gtts", dest="gtts", action='store_true', default=False,
                  help="Compute Global Truth Tables (Default to False). This could take some time for many models.")

    parser.add_option("-o", "--outdir", dest="outdir", default='.',
                    help="Output directory path (Default to current directory)", metavar="O")

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("incorrect number of arguments")

    allowed = [1, 2]
    if options.pvalue not in allowed:
        parser.error("incorrect value for discretization range: %s. Allowed values: %s" % (options.pvalue, allowed))

    if options.qvalue - 2*options.pvalue < 0:
        parser.error("incorrect value for discretization range %s or size penalty %s. They must satisfy q - 2p >= 0" % (options.pvalue, options.qvalue))
    
    allowed_tol = 0.5
    if options.tolerance > allowed_tol or options.tolerance < 0:
        parser.error("incorrect value for tolerance: %s. Allowed values are: 0 <= t <= %s" % (options.tolerance, allowed_tol))
        
    pkn = args[0]
    midas = args[1]
    
    models, score, optsize, data, instance = bioasp.optimize(pkn,midas,options.tolerance,options.pvalue,options.qvalue)
    
    print "\nProcessing %s boolean models..." % len(models)
    hyperedges = bioasp.get_hyperedges(instance)
    matrix = utils.get_matrix(models, hyperedges)
    
    if not os.path.exists(options.outdir):
        os.mkdir(options.outdir)
    
    writer.write_models(matrix, hyperedges, options.outdir)
    writer.write_frequencies(matrix, hyperedges, options.outdir)
    
    exclusives, inclusives = bioasp.get_mutual_hyperedges(models)
    writer.write_mutuals(exclusives, inclusives, options.outdir)
    
    if options.gtts:
        print "\nComputing models equivalences...",
        equivalences = bioasp.get_models_equivalences(models,instance)
        print 'done.'
        clusters = set(equivalences)
        print "\nComputing %s Global Truth Tables..." % len(clusters)
        muples = []
        for c in clusters:
            muples.append((c, utils.get_mse(models[c], data), equivalences.count(c)))
            writer.write_gtt(utils.get_gtt(models[c], data), c, data, options.outdir)
            
        print 'done.'
        print "Wrote %s/gtt-%s.csv" % (options.outdir, list(clusters))
        writer.write_gtt_stats(muples, options.outdir)

    utils.clean_up()
