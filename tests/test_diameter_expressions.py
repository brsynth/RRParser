from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from rrparser import build_args_parser, parse_rules
from rrparser.Args import parse_diameters


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("0,2,4", [0, 2, 4]),
        ("0-8", [0, 2, 4, 6, 8]),
        ("<8", [0, 2, 4, 6]),
        ("<=8", [0, 2, 4, 6, 8]),
        (">8", [10, 12, 14, 16, 18, 20]),
        (">=8", [8, 10, 12, 14, 16, 18, 20]),
        (">20", []),
        (">=20", [20]),
        (">=0", list(range(0, 21, 2))),
        (">9", [10, 12, 14, 16, 18, 20]),
        (">= 18", [18, 20]),
        ("<4,>=18", [0, 2, 18, 20]),
        ("0-8,20,8", [0, 2, 4, 6, 8, 20]),
        ("1-9", [2, 4, 6, 8]),
        (" 0 - 8 ", [0, 2, 4, 6, 8]),
        ("<=0", [0]),
        ("<0", []),
        ("18-20", [18, 20]),
        ("<=20", list(range(0, 21, 2))),
    ],
)
def test_expressions(expression, expected, tmp_path):
    assert parse_diameters(expression) == [diameter // 2 for diameter in expected]
    args = build_args_parser().parse_args(["--diameters", expression])
    rules = tmp_path / "templates.csv"
    pd.DataFrame(
        {
            "TEMPLATE_ID": [f"RR:{radius}" for radius in range(11)],
            "TEMPLATE": ["[C]>>[O]"] * 11,
            "SCORE": [1.0] * 11,
            "ECS": ["1.1.1.1"] * 11,
            "RADII": list(range(11)),
        }
    ).to_csv(rules, index=False)
    output = parse_rules(None, rules_file=str(rules), radii=args.radii)
    assert pd.read_csv(StringIO(output))["Rule ID"].tolist() == [
        f"RR:{diameter // 2}" for diameter in expected
    ]


@pytest.mark.parametrize(
    "expression", ["", "8-0", "2-", "<=x", ">=x", ">>8", "0,,2", "-2"]
)
def test_invalid_expressions(expression):
    with pytest.raises(ValueError):
        parse_diameters(expression)


@pytest.mark.parametrize(
    "expression,enumeration",
    [
        ("0-8", "0,2,4,6,8"),
        ("<8", "0,2,4,6"),
        ("<=8", "0,2,4,6,8"),
        (">8", "10,12,14,16,18,20"),
        (">=8", "8,10,12,14,16,18,20"),
    ],
)
def test_legacy_rules(expression, enumeration):
    rules = str(Path(__file__).parent / "data/rules.csv")
    assert parse_rules(
        None, rules_file=rules, radii=parse_diameters(expression)
    ) == parse_rules(None, rules_file=rules, radii=parse_diameters(enumeration))
