#!/usr/bin/env python

"""
Created on Jun 1, 2012
"""

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__date__ = "Jun 1, 2012"

import unittest
import os

from custodian.vasp.handlers import VaspErrorHandler


test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                        'test_files')


class VaspErrorHandlerTest(unittest.TestCase):

    def test_check_correct(self):
        if "VASP_PSP_DIR" not in os.environ:
            os.environ["VASP_PSP_DIR"] = test_dir
        os.chdir(test_dir)
        h = VaspErrorHandler("vasp.teterror")
        h.check()
        h.correct()
        self.assertEqual(h.errors, set(['tet']))
        self.assertEqual(h.actions,
                         [{'action': {'_set': {'ISMEAR': 0}},
                           'dict': 'INCAR'}])
        h = VaspErrorHandler("vasp.classrotmat")
        h.check()
        h.correct()
        self.assertEqual(h.errors, set(['mesh_symmetry']))
        self.assertEqual(h.actions,
                         [{'action': {'_set': {'kpoints': [[8, 8, 8]]}},
                           'dict': 'KPOINTS'}])
        os.remove("corrections.json")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
