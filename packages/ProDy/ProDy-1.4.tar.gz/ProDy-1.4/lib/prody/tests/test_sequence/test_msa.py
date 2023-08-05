#!/usr/bin/python
# -*- coding: utf-8 -*-
# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2012 Ahmet Bakan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'

from unittest import TestCase

from numpy import array, log, zeros, char
from numpy.testing import assert_array_equal, assert_array_almost_equal

from prody.tests.test_datafiles import *

from prody import LOGGER, refineMSA, parseMSA, calcMSAOccupancy

LOGGER.verbosity = None

FASTA = parseMSA(pathDatafile('msa_Cys_knot.fasta'))
FASTA_ALPHA = char.isalpha(FASTA._msa) 

class TestRefinement(TestCase):


    def testLabel(self):
        label = 'FSHB_BOVIN'
        index = FASTA.getIndex(label)
        refined = refineMSA(FASTA, label=label)._getArray()
        
        expected = FASTA._getArray().take(FASTA_ALPHA[index].nonzero()[0], 1)
        
        assert_array_equal(refined, expected)
        
        
    def testRowocc(self):

        refined = refineMSA(FASTA, row_occ=0.9)._getArray()
        expected = FASTA._getArray()[FASTA_ALPHA.sum(1) / 112. >= 0.9,:]
        
        assert_array_equal(refined, expected)
        
    def testColocc(self):
        
        refined = refineMSA(FASTA, col_occ=0.9)._getArray()
        expected = FASTA._getArray()[:, FASTA_ALPHA.sum(0) / 24. >= 0.9]
        
        assert_array_equal(refined, expected)
        
    def testRowCol(self):
        
        row_occ = 0.9 
        col_occ = 1.0 
        refined = refineMSA(FASTA, row_occ=row_occ,
                            col_occ=col_occ)._getArray()
        rows = FASTA_ALPHA.sum(1) / 112. >= row_occ
        expected = FASTA._getArray()[rows]
        cols = char.isalpha(expected).sum(0, 
                    dtype=float) / expected.shape[0] >= col_occ 
        
        expected = expected.take(cols.nonzero()[0], 1)
        assert_array_equal(refined, expected)


    def testAll(self):

        row_occ = 0.9 
        col_occ = 0.9 
        label = 'FSHB_BOVIN'
        refined = refineMSA(FASTA, label=label, 
                            row_occ=row_occ, col_occ=col_occ)

        index = FASTA.getIndex(label)
        which = FASTA_ALPHA[index].nonzero()[0]
        expected = FASTA._getArray().take(which, 1)
        
        expected = expected[calcMSAOccupancy(expected, 'row') >= row_occ]
        
        which = (calcMSAOccupancy(expected) >= col_occ).nonzero()[0]
        expected = expected.take(which, 1)

        assert_array_equal(refined._getArray(), expected)
