"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from unittest import TestCase

# Specific for tool
from sys import path as sys_path
from os import path as os_path
from rrparser import Parser

# Specific for tests themselves
from os import stat
from itertools import combinations
from random import sample, seed
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from tarfile import open as tf_open


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR(TestCase):

    def setUp(self):
        self.diameters = ['2', '4', '6', '8', '10', '12', '14', '16']
        self.rr_parser = Parser()
        self.hash_d2 = 'a6c2852a991e394bdbaf04791a90e803d4410a53f037165a7f08956edde63066'

    # 'test_' prefix is mandatory
    def test_Precedence(self):
        diam = '2'
        tempdir = TemporaryDirectory(suffix='_'+diam)
        outfile = self.rr_parser.parse_rules(outdir=tempdir.name,
                                             rules_file='tests/data/rules.csv',
                                             rule_type='retro',
                                             diameters=diam)
        self.assertEqual(
            sha256(Path(outfile).read_bytes()).hexdigest(),
            'a6c2852a991e394bdbaf04791a90e803d4410a53f037165a7f08956edde63066'
                        )
        tempdir.cleanup()

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

    def test_SmallRulesFile_OneDiameter_SpecifyOutfile(self):
        hash = 'a6c2852a991e394bdbaf04791a90e803d4410a53f037165a7f08956edde63066'
        for format in ['csv', 'tar.gz']:
            with self.subTest(format=format):
                diam = '2'
                tempdir = TemporaryDirectory(suffix='_'+diam)
                outfile = self.rr_parser.parse_rules(outfile='./results.'+format,
                                                     rules_file='tests/data/rules.csv',
                                                     diameters=diam,
                                                     output_format=format)
                if format=='tar.gz':
                    tar = tf_open(outfile)
                    tar.extractall()
                    tar.close()
                    outfile = 'rules_d2.csv'
                self.assertEqual(
                    sha256(Path(outfile).read_bytes()).hexdigest(), self.hash_d2)
                tempdir.cleanup()

    def test_BadRuleTypeArgument(self):
        for rule_type in ['test', 'reto']:
            with self.subTest(rule_type=rule_type):
                tempdir = TemporaryDirectory(suffix='_'+rule_type+'_2')
                self.assertRaises(ValueError,
                                  self.rr_parser.parse_rules,
                                            outdir=tempdir.name,
                                            rule_type=rule_type,
                                            diameters='2')
                tempdir.cleanup()

    def test_EmptyRuleTypeArgument(self):
        for rule_type in ['']:
            with self.subTest(rule_type=rule_type):
                tempdir = TemporaryDirectory(suffix='_'+rule_type+'_2')
                self.assertRaises(ValueError,
                                  self.rr_parser.parse_rules,
                                            outdir=tempdir.name,
                                            rule_type=rule_type,
                                            diameters='2')
                tempdir.cleanup()

    def test_BadDiametersArgument(self):
        for diam in ['3']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_retro_'+diam)
                outfile = self.rr_parser.parse_rules(outdir=tempdir.name,
                                                     rule_type='retro',
                                                     diameters=diam)
                self.assertEqual(stat(outfile).st_size, 135)
                tempdir.cleanup()

    def test_OneDiameter(self):
        for diam in ['2']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_retro_'+diam)
                outfile = self.rr_parser.parse_rules(outdir=tempdir.name,
                                                     rule_type='retro',
                                                     diameters=diam)
                self.assertEqual(
                    sha256(Path(outfile).read_bytes()).hexdigest(),
            '68cca7d6b890676d62ef0d950db3ce9a1ca5f991e54d91932e551b4fb42ff709'
                                )
                tempdir.cleanup()

    def test_MiscDiametersArgument(self):
        for diam in ['2-']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_retro_'+diam)
                outfile = self.rr_parser.parse_rules(outdir=tempdir.name,
                                                     rule_type='retro',
                                                     diameters=diam)
                self.assertEqual(stat(outfile).st_size, 135)
                tempdir.cleanup()

    def test_AllTypes_RandomDiam(self):
        for rule_type in ['all', 'retro', 'forward']:
            for i in range(len(self.diameters)):
                diams = list(combinations(self.diameters, i+1))
                seed(2)
                sub_diams = sample(diams, 1)
                for diam in sub_diams:
                    with self.subTest(rule_type=rule_type, diam=diam):
                        tempdir = TemporaryDirectory(suffix='_'+rule_type+'_'+'-'.join(diam))
                        outfile = self.rr_parser.parse_rules(outdir=tempdir.name,
                                                             rule_type=rule_type,
                                                             diameters=','.join(diam))
                        self.assertGreater(stat(outfile).st_size, 135)
                        tempdir.cleanup()
