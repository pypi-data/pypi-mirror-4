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

from glob import glob
from os import remove
from os.path import join

from prody.tests.test_datafiles import TEMPDIR
from prody.utilities import gunzip, openFile


class TestGunzip(TestCase):
    
    def setUp(self):
        
        self.pref = join(TEMPDIR, 'compressed.txt')
        self.gzfn = self.pref + '.gz' 
        self.text = '\n'.join(['some random text'] * 100)
        with openFile(self.gzfn, 'w') as out:
            out.write(self.text)
        
    def testFile(self):
        
        self.assertEqual(open(gunzip(self.gzfn)).read(), self.text)

    def testBuffer(self):
        
        self.assertEqual(gunzip(open(self.gzfn).read()), self.text)
        
    def tearDown(self):
        
        for fn in glob(self.pref + '*'):
            remove(fn)
