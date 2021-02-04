"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from test_light import Test_RR

# Specific for tool
from rrparser.Parser import parse_rules

# Specific for tests themselves
from io       import open as io_open
from tempfile import NamedTemporaryFile



# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR_Diameters(Test_RR):


    def test_BadDiametersArgument(self):
        for diam in ['3']:
            with self.subTest(diam=diam):
                outfile = NamedTemporaryFile(delete=True)
                parse_rules(
                    rules_file=self.rules_file,
                    rule_type='retro',
                    diameters=diam,
                    outfile=outfile.name
                )
                # Test if outfile has one single line (header)
                self.assertEqual(len(outfile.readlines()), 1)
                outfile.close()

    def test_OneDiameter(self):
        for diam in ['2']:
            with self.subTest(diam=diam):
                outfile = NamedTemporaryFile(delete=True)
                parse_rules(
                    rules_file=self.rules_file,
                    diameters=diam,
                    outfile=outfile.name
                )
                self.assertListEqual(
                    list(io_open(outfile.name)),
                    list(io_open(self.ref_d2_csv))
                )
                outfile.close()

    def test_MiscDiametersArgument(self):
        for diam in ['2-']:
            with self.subTest(diam=diam):
                outfile = NamedTemporaryFile(delete=True)
                self.assertRaises(
                    ValueError,
                    parse_rules,
                        rules_file='retrorules',
                        diameters=diam,
                        outfile=outfile.name
                )
