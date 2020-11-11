"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from Test_RR import Test_RR

# Specific for tool
from rrparser import Parser

# Specific for tests themselves
from hashlib  import sha256
from pathlib  import Path
from tempfile import TemporaryDirectory
from os       import stat, remove



# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR_Diameters(Test_RR):

    def test_BadDiametersArgument(self):
        for diam in ['3']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_retro_'+diam)
                outfile = self.rr_parser.parse_rules(outdir=tempdir.name,
                                                     rule_type='retro',
                                                     diameters=diam)
                self.assertEqual(stat(outfile).st_size, 135)
                remove(outfile)
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
                remove(outfile)
                tempdir.cleanup()

    def test_MiscDiametersArgument(self):
        for diam in ['2-']:
            with self.subTest(diam=diam):
                tempdir = TemporaryDirectory(suffix='_retro_'+diam)
                self.assertRaises(ValueError,
                                  self.rr_parser.parse_rules,
                                  outdir=tempdir.name,
                                  rule_type='retro',
                                  diameters=diam)
                tempdir.cleanup()
