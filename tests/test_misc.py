"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from test_light import Test_RR

# Specific for tool
from sys      import path as sys_path
from os       import path as os_path
from rrparser import parse_rules

# Specific for tests themselves
from os        import stat
from itertools import combinations
from random    import sample, seed
from io        import open as io_open
from tempfile  import NamedTemporaryFile
from tarfile   import open as tf_open


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_Misc(Test_RR):

    # # 'test_' prefix is mandatory
    # def test_Precedence(self):
    #     diam = '2'
    #     tempdir = TemporaryDirectory(suffix='_'+diam)
    #     outfile = self.rr_parser.parse_rules(outdir=tempdir.name,
    #                                          rules_file='data/rules.csv',
    #                                          rule_type='retro',
    #                                          diameters=diam)
    #     self.assertEqual(
    #         sha256(Path(outfile).read_bytes()).hexdigest(), self.hash_d2_csv)

    def test_SmallRulesFile_OneDiameter_SpecifyOutfile(self):
        for format in ['csv', 'tsv']:
            with self.subTest(format=format):
                diam = '2'
                outfile = NamedTemporaryFile(delete=True)
                parse_rules(
                    rules_file    = 'data/rules.csv',
                    outfile       = outfile.name,
                    diameters     = diam,
                    output_format = format
                )
                self.assertListEqual(
                    list(
                        io_open(
                            outfile.name
                        )
                    ),
                    list(
                        io_open(
                            getattr(
                                self,
                                'ref_d2_'+format
                            )
                        )
                    )
                )
                outfile.close()


    def test_AllTypes_RandomDiam(self):
        for rule_type in ['all', 'retro', 'forward']:
            # for i in range(len(self.diameters)):
            i = 3
            diams = list(
                combinations(
                    self.diameters,
                    i+1
                )
            )
            seed(2)
            sub_diams = sample(diams, 1)
            for diam in sub_diams:
                with self.subTest(rule_type=rule_type, diam=diam):
                    outfile = NamedTemporaryFile(delete=True)
                    parse_rules(
                        rules_file = 'retrorules',
                        outfile    = outfile.name,
                        rule_type  = rule_type,
                        diameters  = ','.join(diam)
                    )
                    # Test if outfile has more than one single line (header)
                    self.assertGreater(
                        len(outfile.readlines()),
                        1
                    )
                    outfile.close()
