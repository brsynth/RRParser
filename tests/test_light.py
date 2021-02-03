"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from unittest import TestCase

# Specific for tool
from rrparser import parse_rules

# Specific for tests themselves
from hashlib  import sha256
from pathlib  import Path
from tempfile import NamedTemporaryFile



# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR(TestCase):


    def setUp(self):
        self.diameters   = ['2', '4', '6', '8', '10', '12', '14', '16']
        self.hash_d2_csv = 'f0c895aebd9527ce29142a10ee41375b05ea91d02a7cc1042b88407bc6a60516'
        self.hash_d2_tsv = '0cc7db25f78edda00894158559cbca79ce67074167431592860fe14072608b78'


    def test_SmallRulesFile_OneDiameter(self):
        for diam in ['2,4,6']:
            with self.subTest(diam=diam):
                outfile = NamedTemporaryFile(delete=True)
                parse_rules(rules_file='data/rules.csv',
                            diameters=diam,
                            outfile=outfile.name)
                self.assertEqual(
                    sha256(Path(outfile.name).read_bytes()).hexdigest(), self.hash_d2_csv)
                outfile.close()


    def test_GoodInputFormatCSV(self):
        diam = '2'
        outfile = NamedTemporaryFile(delete=True)
        parse_rules(rules_file='data/rules.csv',
                    input_format='csv',
                    diameters=diam,
                    outfile=outfile.name)
        self.assertEqual(
            sha256(Path(outfile.name).read_bytes()).hexdigest(), self.hash_d2_csv)
        outfile.close()


    # def test_BadInputFormatCSV_1(self):
    #     diam = '2'
    #     outfile = NamedTemporaryFile(suffix='_'+diam, delete=True)
    #     self.assertRaises(KeyError,
    #                       parse_rules,
    #                       rules_file='data/rules.csv',
    #                       input_format='tsv',
    #                       diameters=diam,
    #                       outfile=outfile.name)
    #     outfile.close()
    #
    def test_BadInputFormatCSV_2(self):
        diam = '2'
        outfile = NamedTemporaryFile(delete=True)
        self.assertRaises(ValueError,
                          parse_rules,
                          rules_file='data/rules.csv',
                          input_format='other',
                          diameters=diam,
                          outfile=outfile.name)
        outfile.close()
