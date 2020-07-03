"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from unittest import TestCase

# Specific for tool
from rrparser import Parser

# Specific for tests themselves
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory


# sys_path.insert(0, os_path.dirname(__file__)+'/rrparser')


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR(TestCase):

    def setUp(self):
        self.diameters = ['2', '4', '6', '8', '10', '12', '14', '16']
        self.rr_parser = Parser()

    def test_SmallRulesFile_OneDiameter(self):
        for diam in ['2']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_'+diam)
                outfile = self.rr_parser.parse_rules(outdir=tempdir.name,
                                                     rules_file='tests/data/rules.csv',
                                                     diameters=diam)
                self.assertEqual(
                    sha256(Path(outfile).read_bytes()).hexdigest(),
            'a6c2852a991e394bdbaf04791a90e803d4410a53f037165a7f08956edde63066'
                                )
                tempdir.cleanup()

    # def test_SmallRulesFile_OneDiameter_WithFingerPrint(self):
    #     for diam in ['2']:
    #         with self.subTest(diam=diam):
    #             tempdir = mkdtemp(suffix='_'+diam)
    #             outfile = self.rr_parser.parse_rules(outdir=tempdir,
    #                                                  rules_file='tests/data/rules.csv',
    #                                                  diameters=diam)
    #             self.assertEqual(
    #                 sha256(Path(outfile).read_bytes()).hexdigest(),
    #         'a6c2852a991e394bdbaf04791a90e803d4410a53f037165a7f08956edde63066'
    #                             )
