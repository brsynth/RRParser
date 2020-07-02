"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from unittest import TestCase

# Specific for tool
from sys import path as sys_path
from os import path as os_path
from RRulesParser import RRulesParser

# Specific for tests themselves
from os import stat
from itertools import combinations
from random import sample, seed
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory


sys_path.insert(0, os_path.dirname(__file__)+'/..')


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR(TestCase):

    def setUp(self):
        self.diameters = ['2', '4', '6', '8', '10', '12', '14', '16']
        self.RRulesParser = RRulesParser()

    def test_my_function(benchmark):
        result = benchmark(test)

    # 'test_' prefix is mandatory
    def test_RetroRules__BadRuleTypeArgument(self):
        for rule_type in ['test', 'reto']:
            with self.subTest(rule_type=rule_type):
                tempdir = TemporaryDirectory(suffix='_'+rule_type+'_2')
                self.assertRaises(ValueError,
                                  self.RRulesParser.parse_rules,
                                            outdir=tempdir.name,
                                            rule_type=rule_type,
                                            diameters='2')
                tempdir.cleanup()

    def test_RetroRules__EmptyRuleTypeArgument(self):
        for rule_type in ['']:
            with self.subTest(rule_type=rule_type):
                tempdir = TemporaryDirectory(suffix='_'+rule_type+'_2')
                self.assertRaises(ValueError,
                                  self.RRulesParser.parse_rules,
                                            outdir=tempdir.name,
                                            rule_type=rule_type,
                                            diameters='2')
                tempdir.cleanup()

    def test_RetroRules__BadDiametersArgument(self):
        for diam in ['3']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_retro_'+diam)
                outfile = self.RRulesParser.parse_rules(outdir=tempdir.name,
                                                     rule_type='retro',
                                                     diameters=diam)
                self.assertEqual(stat(outfile).st_size, 135)
                tempdir.cleanup()

    def test_RetroRules__OneDiameter(self):
        for diam in ['2']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_retro_'+diam)
                outfile = self.RRulesParser.parse_rules(outdir=tempdir.name,
                                                     rule_type='retro',
                                                     diameters=diam)
                self.assertEqual(
                    sha256(Path(outfile).read_bytes()).hexdigest(),
            '68cca7d6b890676d62ef0d950db3ce9a1ca5f991e54d91932e551b4fb42ff709'
                                )
                tempdir.cleanup()

    def test_RetroRules__MiscDiametersArgument(self):
        for diam in ['2-']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_retro_'+diam)
                outfile = self.RRulesParser.parse_rules(outdir=tempdir.name,
                                                     rule_type='retro',
                                                     diameters=diam)
                self.assertEqual(stat(outfile).st_size, 135)
                tempdir.cleanup()

    def test_RetroRules__AllTypes_RandomDiam(self):
        for rule_type in ['all', 'retro', 'forward']:
            for i in range(len(self.diameters)):
                diams = list(combinations(self.diameters, i+1))
                seed(2)
                sub_diams = sample(diams, 1)
                for diam in sub_diams:
                    with self.subTest(rule_type=rule_type, diam=diam):
                        tempdir = TemporaryDirectory(suffix='_'+rule_type+'_'+'-'.join(diam))
                        outfile = self.RRulesParser.parse_rules(outdir=tempdir.name,
                                                             rule_type=rule_type,
                                                             diameters=','.join(diam))
                        self.assertGreater(stat(outfile).st_size, 135)
                        tempdir.cleanup()
