"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from test_light import Test_RR

# Specific for tool
from rrparser.Parser import (
    parse_rules,
    fetch_retrorules
)

# Specific for tests themselves
from hashlib  import sha256
from pathlib  import Path
from tempfile import NamedTemporaryFile



# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR_Diameters(Test_RR):

    def test_BadDiametersArgument(self):
        for diam in ['3']:
            with self.subTest(diam=diam):
                outfile = NamedTemporaryFile(delete=True)
                rule_type = 'retro'
                parse_rules(rules_file=fetch_retrorules(),
                            rule_type=rule_type,
                            diameters=diam,
                            outfile=outfile.name)
                # Test if outfile has one single line (header)
                self.assertEqual(len(outfile.readlines()), 1)
                outfile.close()

    def test_OneDiameter(self):
        for diam in ['2']:
            with self.subTest(diam=diam):
                outfile = NamedTemporaryFile(delete=True)
                parse_rules(rules_file=fetch_retrorules(),
                            diameters=diam,
                            outfile=outfile.name)
                self.assertEqual(
                    sha256(Path(outfile.name).read_bytes()).hexdigest(),
                    '2dce58b7fa06fa31d93aca63eccd7f65c8b8dda4dc7c885425532b0d4b0856b9'
                                )
                outfile.close()

    def test_MiscDiametersArgument(self):
        for diam in ['2-']:
            with self.subTest(diam=diam):
                outfile = NamedTemporaryFile(delete=True)
                self.assertRaises(ValueError,
                                  parse_rules,
                                  rules_file=fetch_retrorules(),
                                  diameters=diam,
                                  outfile=outfile.name)
