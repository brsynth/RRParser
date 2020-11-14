"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from test_RR import Test_RR

# Specific for tool
from rrparser import parse_rules, fetch_retrorules

# Specific for tests themselves
from hashlib  import sha256
from pathlib  import Path
from tempfile import NamedTemporaryFile



# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR_RuleType(Test_RR):

    def test_BadRuleTypeArgument(self):
        for rule_type in ['test', 'reto']:
            with self.subTest(rule_type=rule_type):
                outfile = NamedTemporaryFile(suffix='_'+rule_type+'_2', delete=True)
                self.assertRaises(ValueError,
                                  parse_rules,
                                  rules_file=fetch_retrorules(rule_type),
                                  outfile=outfile.name,
                                  rule_type=rule_type,
                                  diameters='2')

    def test_EmptyRuleTypeArgument(self):
        for rule_type in ['']:
            with self.subTest(rule_type=rule_type):
                tempdir = TemporaryDirectory(suffix='_'+rule_type+'_2')
                self.assertRaises(ValueError,
                                  self.rr_parser.parse_rules,
                                            outdir=tempdir.name,
                                            rule_type=rule_type,
                                            diameters='2')
