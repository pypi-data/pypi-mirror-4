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
from cellnopt.wrapper import *

def compress(pkn, midas):
    """
    Compress a PKN with respect to a MIDAS file using CellNOpt. 
    Returns the SIF filepath to the compressed PKN
    
    :param pkn: PKN sif filepath
    :param midas: MIDAS filepath
    :returns: string
    """
    temp = ".compr_model.sif"
    if os.path.exists(temp):
        os.remove(temp)
    
    cnolist = CNOlist(midas)
    pknmodel = readSIF(pkn)        
    model = preprocessing(cnolist, pknmodel, expansion=False)
    writeSIF(model, temp)
    
    return temp