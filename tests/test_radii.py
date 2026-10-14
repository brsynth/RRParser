import logging
from io import StringIO

import pandas as pd
import pytest

from rrparser import build_args_parser, parse_diameters, parse_radii, parse_rules


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("0,2,4", [0, 2, 4]),
        ("0-8", list(range(9))),
        ("<8", list(range(8))),
        ("<=8", list(range(9))),
        (">8", [9, 10]),
        (">=8", [8, 9, 10]),
        ("0-2,8,>=10", [0, 1, 2, 8, 10]),
        (" 1 - 3 , 3 ", [1, 2, 3]),
        ("<0", []),
        (">10", []),
        (">=10", [10]),
        ("<=10", list(range(11))),
    ],
)
def test_radius_expressions_select_templates(tmp_path, expression, expected):
    assert parse_radii(expression) == expected
    args = build_args_parser().parse_args(["--radii", expression])
    assert args.radii == expected
    assert not hasattr(args, "diameters")
    source = tmp_path / "templates.csv"
    pd.DataFrame(
        {
            "TEMPLATE_ID": [f"RR:{radius}" for radius in range(11)],
            "TEMPLATE": ["[C]>>[O]"] * 11,
            "SCORE": [1.0] * 11,
            "ECS": ["1.1.1.1"] * 11,
            "RADII": list(range(11)),
        }
    ).to_csv(source, index=False)
    result = parse_rules(None, rules_file=str(source), radii=args.radii)
    assert pd.read_csv(StringIO(result))["Rule ID"].tolist() == [
        f"RR:{radius}" for radius in expected
    ]


@pytest.mark.parametrize(
    "option,expression,expected",
    [
        ("--radii", "0-4", [0, 1, 2, 3, 4]),
        ("--radii", "<=4", [0, 1, 2, 3, 4]),
        ("--diameters", "0-8", [0, 1, 2, 3, 4]),
        ("-d", "<=8", [0, 1, 2, 3, 4]),
        ("--radii", ">=8", [8, 9, 10]),
        ("--diameters", ">=16", [8, 9, 10]),
    ],
)
def test_cli_only_passes_normalized_radii(monkeypatch, option, expression, expected):
    from unittest.mock import Mock

    from rrparser import __main__ as cli

    parse = Mock(return_value=None)
    monkeypatch.setattr(cli, "parse_rules", parse)
    monkeypatch.setattr(cli, "create_logger", lambda *args: logging.getLogger("test"))
    monkeypatch.setattr("sys.argv", ["rrparser", option, expression, "-o", "rules.csv"])
    cli.entry_point()
    kwargs = parse.call_args[1]
    assert kwargs["radii"] == expected
    assert "diameters" not in kwargs


@pytest.mark.parametrize(
    "option,expression",
    [
        ("--radii", "11"),
        ("--radii", "2-"),
        ("--radii", "4-0"),
        ("--radii", "1.5"),
        ("--radii", "-1"),
        ("--radii", ""),
        ("--diameters", "3"),
        ("--diameters", "22"),
    ],
)
def test_invalid_expressions_fail_before_parsing(monkeypatch, option, expression):
    from unittest.mock import Mock

    from rrparser import __main__ as cli

    parse = Mock()
    monkeypatch.setattr(cli, "parse_rules", parse)
    monkeypatch.setattr("sys.argv", ["rrparser", option, expression])
    with pytest.raises(SystemExit) as error:
        cli.entry_point()
    assert error.value.code == 2
    parse.assert_not_called()


@pytest.mark.parametrize("radii", [[-1], [11], [1.5], [True]])
def test_api_validates_normalized_radii_before_download(radii):
    with pytest.raises(ValueError, match="Radii must be integers"):
        parse_rules(None, radii=radii)


def test_defaults_and_empty_selection():
    args = build_args_parser().parse_args([])
    assert list(args.radii) == list(range(11))
    assert parse_diameters("<0") == parse_radii("<0") == []
