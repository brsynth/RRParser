from pathlib import Path
from tempfile import TemporaryDirectory

from test_main import Test_RR

from rrparser import parse_rules
from rrparser.Args import parse_diameters


class Test_RR_Light(Test_RR):
    def test_GoodInputFormatCSV(self):
        # Do not keep an output file handle open while pandas writes it.
        with TemporaryDirectory() as directory:
            outfile = Path(directory) / "rules.csv"
            parse_rules(
                str(outfile),
                rules_file=self.rules_file,
                input_format="csv",
                radii=parse_diameters("2"),
            )
            self.assertEqual(outfile.read_text(), Path(self.ref_d2_csv).read_text())

    def test_BadInputFormatCSV_1(self):
        self.assertRaises(
            KeyError,
            parse_rules,
            None,
            rules_file=self.rules_file,
            input_format="tsv",
            radii=parse_diameters("2"),
        )

    def test_BadInputFormatCSV_2(self):
        self.assertRaises(
            ValueError,
            parse_rules,
            None,
            rules_file=self.rules_file,
            input_format="other",
            radii=parse_diameters("2"),
        )
