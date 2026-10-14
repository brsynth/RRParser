"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process

# Specific for tool

# Specific for tests themselves
from pathlib import Path
from tarfile import open as open_tar
from tempfile import TemporaryDirectory
from unittest.mock import patch

from pandas import read_csv
from test_main import Test_RR

from rrparser import parse_rules
from rrparser.Args import parse_diameters
from rrparser.Downloads import RR02_CACHE_FILE, RR02_FILE


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_Misc(Test_RR):
    def test_SmallRulesFile_OneDiameter_SpecifyOutfile(self):
        with TemporaryDirectory() as directory:
            for format in ["csv", "tsv"]:
                with self.subTest(format=format):
                    outfile = Path(directory) / ("rules." + format)
                    parse_rules(
                        str(outfile),
                        rules_file=self.rules_file,
                        radii=parse_diameters("2"),
                        output_format=format,
                    )
                    reference = Path(getattr(self, "ref_d2_" + format))
                    self.assertEqual(outfile.read_text(), reference.read_text())

    def test_AllTypes_CachedRR02(self):
        diameters = [2, 4, 8, 14]
        with TemporaryDirectory() as directory:
            cache = Path(directory) / "cache"
            cache.mkdir()
            with open_tar(cache / RR02_CACHE_FILE, mode="w:gz") as archive:
                archive.add(self.rules_file, arcname=RR02_FILE)
            outfile = Path(directory) / "rules.csv"
            with patch(
                "rrparser.Downloads.urlopen", side_effect=AssertionError("Network used")
            ):
                for rule_type in ["all", "retro", "forward"]:
                    with self.subTest(rule_type=rule_type):
                        parse_rules(
                            outfile=str(outfile),
                            rules_dir=str(cache),
                            release="rr02",
                            rule_type=rule_type,
                            radii=parse_diameters(",".join(map(str, diameters))),
                        )
                        results = read_csv(outfile)
                        self.assertFalse(results.empty)
                        self.assertTrue(set(results["Diameter"]).issubset(diameters))
                        if rule_type != "all":
                            self.assertTrue(
                                set(results["Rule usage"]).issubset({"both", rule_type})
                            )
