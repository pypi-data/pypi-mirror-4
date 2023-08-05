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
import csv

def write_csv(iterable, header, filename, rowmaker=lambda r: r, verbose=True):
    f = open(filename, 'w')
    writer = csv.DictWriter(f, header)
    writer.writeheader()
    for row in iterable:
        writer.writerow(rowmaker(row))
    f.close()
    if verbose:
        print "Wrote %s" % filename

def write_models(matrix, hyperedges, outdir):
    write_csv(matrix, hyperedges, outdir + '/models.csv')

def write_frequencies(matrix, hyperedges, outdir):
    def rowmaker(row):
        nmodels = len(matrix)
        oc = 0.
    	for r in matrix:
        	oc = oc + r[row]
    	return dict(hyperedge = row, frequency=oc/nmodels)
    	
    write_csv(hyperedges, ['hyperedge','frequency'], outdir + '/frequencies.csv', rowmaker)

def write_gtt(gtt, idmodel, data, outdir):
    header = data.stimulus + map(lambda i: i+'i', data.inhibitors) + data.readouts
    write_csv(gtt, header, outdir + '/gtt-%s.csv' % idmodel, verbose=False)
    
def write_gtt_stats(models, outdir):
    rowmaker = lambda r: dict(id=r[0], mse="%.4f" % r[1], models=r[2])
    write_csv(models, ['id','mse','models'], outdir + '/gtt_stats.csv', rowmaker)
	
def write_mutuals(exclusives, inclusives, outdir):
    rowmaker = lambda r: dict(hyperedge_a = r[0], frequency_a = "%.4f" % r[1], hyperedge_b = r[2], frequency_b = "%.4f" % r[3])
    header = ['hyperedge_a', 'frequency_a', 'hyperedge_b', 'frequency_b']
    write_csv(exclusives, header, outdir + '/exclusives.csv', rowmaker)
    write_csv(inclusives, header, outdir + '/inclusives.csv', rowmaker)