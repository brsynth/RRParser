"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from test_light import Test_RR

# Specific for tool
from rrparser import parse_rules

# Specific for tests themselves
from hashlib  import sha256
from pathlib  import Path
from tempfile import NamedTemporaryFile



# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR_InputFormat(Test_RR):


    # def test_GoodInputFormatCSV(self):
    #     diam = '2'
    #     outfile = NamedTemporaryFile(delete=True)
    #     parse_rules(rules_file='data/rules.csv',
    #                 input_format='csv',
    #                 rule_type='retro',
    #                 diameters=diam,
    #                 outfile=outfile.name)
    #     self.assertEqual(
    #         sha256(Path(outfile.name).read_bytes()).hexdigest(), self.hash_d2_csv)
    #     outfile.close()


    def test_BadInputFormatCSV_1(self):
        diam = '2'
        outfile = NamedTemporaryFile(delete=True)
        self.assertRaises(
            KeyError,
            parse_rules,
                rules_file='data/rules.csv',
                input_format='tsv',
                diameters=diam,
                outfile=outfile.name
        )
        outfile.close()


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


    # def test_SmallRulesFile_OneDiameter_WithFingerPrint(self):
    #     for diam in ['2']:
    #         with self.subTest(diam=diam):
    #             tempdir = mkdtemp(suffix='_'+diam)
    #             outfile = self.rr_parser.parse_rules(outdir=tempdir,
    #                                                  rules_file='data/rules.csv',
    #                                                  diameters=diam)
    #             self.assertEqual(
    #                 sha256(Path(outfile).read_bytes()).hexdigest(),
    #         'a6c2852a991e394bdbaf04791a90e803d4410a53f037165a7f08956edde63066'
    #                             )
