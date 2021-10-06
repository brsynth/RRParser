"""
Created on June 17 2020

@author: Joan Hérisson
"""
from os import unlink

# Generic for test process
from test_main import Test_RR

# Specific for tool
from rrparser import (
    parse_rules,
    __path__ as pkg_path
)

# Specific for tests themselves
from io import open as io_open
from tempfile import NamedTemporaryFile


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR_Light(Test_RR):


    # def test_SmallRulesFile_OneDiameter(self):
    #     for diam in ['2,4,6']:
    #         with self.subTest(diam=diam):
    #             outfile = NamedTemporaryFile(delete=True)
    #             parse_rules(
    #                 rules_file='data/rules.csv',
    #                 diameters=diam,
    #                 outfile=outfile.name
    #             )
    #             self.assertEqual(
    #                 sha256(
    #                     Path(outfile.name).read_bytes()
    #                 ).hexdigest(),
    #                 self.hash_d2_csv
    #             )
    #             outfile.close()


    def test_GoodInputFormatCSV(self):
        diam = '2'
        outfile = NamedTemporaryFile(delete=False)
        parse_rules(
            rules_file   = self.rules_file,
            input_format = 'csv',
            diameters    = diam,
            outfile      = outfile.name
        )
        self.assertListEqual(
            list(io_open(outfile.name)),
            list(io_open(self.ref_d2_csv))
        )
        outfile.close()
        unlink(outfile.name)


    def test_BadInputFormatCSV_1(self):
        diam = '2'
        outfile = NamedTemporaryFile(suffix='_'+diam, delete=True)
        self.assertRaises(
            KeyError,
            parse_rules,
                rules_file   = self.rules_file,
                input_format = 'tsv',
                diameters    = diam,
                outfile      = outfile.name)
        outfile.close()
    

    def test_BadInputFormatCSV_2(self):
        diam = '2'
        outfile = NamedTemporaryFile(delete=True)
        self.assertRaises(
            ValueError,
            parse_rules,
                rules_file   = self.rules_file,
                input_format = 'other',
                diameters    = diam,
                outfile      = outfile.name
        )
        outfile.close()
