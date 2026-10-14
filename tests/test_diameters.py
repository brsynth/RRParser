from pathlib import Path
from tempfile import TemporaryDirectory

from test_main import Test_RR

from rrparser.Args import parse_diameters
from rrparser.Parser import parse_rules


class Test_RR_Diameters(Test_RR):
    def test_BadDiametersArgument(self):
        self.assertRaises(ValueError, parse_diameters, "3")

    def test_OneDiameter(self):
        # A closed path can be reopened by pandas on Windows.
        with TemporaryDirectory() as directory:
            outfile = Path(directory) / "rules.csv"
            parse_rules(
                str(outfile), rules_file=self.rules_file, radii=parse_diameters("2")
            )
            self.assertEqual(outfile.read_text(), Path(self.ref_d2_csv).read_text())

    def test_MiscDiametersArgument(self):
        self.assertRaises(ValueError, parse_diameters, "2-")
