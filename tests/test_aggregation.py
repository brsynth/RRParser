import gzip
from io import BytesIO, StringIO
from unittest.mock import patch

import pandas as pd
import pytest

from rrparser import build_args_parser, parse_rules
from rrparser.Args import parse_radii
from rrparser.Downloads import fetch_datasets


def cache_dataset(cache, version, name, rows):
    frame = pd.DataFrame(
        rows, columns=["TEMPLATE_ID", "TEMPLATE", "RADII", "SCORE", "ECS", "REACTIONS"]
    )
    frame["DATASETS"] = name
    frame["VALID"] = True
    for column in ("REACTIONS", "ECS"):
        frame[column + "_COUNT"] = frame[column].map(
            lambda value: len(value.split(";")) if value else 0
        )
    frame["RADIUS_MIN"] = frame["RADII"].map(
        lambda value: min(map(int, value.split(";")))
    )
    frame["RADIUS_MAX"] = frame["RADII"].map(
        lambda value: max(map(int, value.split(";")))
    )
    filename = cache / f"retrorules-{version}-{name}.csv.gz"
    filename.write_bytes(gzip.compress(frame.to_csv(index=False).encode()))
    return filename


@pytest.mark.parametrize(
    "selection", ["metanetx,rhea", "rhea+metanetx", "metanetx,rhea,metanetx"]
)
def test_cached_datasets_are_merged_before_filtering(tmp_path, selection):
    sources = [
        cache_dataset(
            tmp_path,
            "3.1.0",
            "metanetx",
            [
                ("shared", "[C]>>[O]", "0;1", 0.2, "1.1", "MNXR1"),
                ("mnx", "[N]>>[O]", "9", 0.5, "3.1", "MNXR2"),
            ],
        ),
        cache_dataset(
            tmp_path,
            "3.1.0",
            "rhea",
            [
                ("shared", "[C]>>[O]", "1;10", 0.8, "2.2", "RHEA:1"),
                ("rhea", "[O]>>[N]", "5", 0.4, "4.1", "RHEA:2"),
            ],
        ),
    ]
    originals = [source.read_bytes() for source in sources]
    args = build_args_parser().parse_args(["--dataset", selection])
    with patch(
        "rrparser.Downloads.urlopen", side_effect=AssertionError("Network used")
    ):
        output = parse_rules(None, rules_dir=str(tmp_path), dataset=args.dataset)
        filtered = parse_rules(
            None,
            rules_dir=str(tmp_path),
            dataset=selection,
            radii=parse_radii("10"),
            ec=["1.1"],
        )
    frame = pd.read_csv(StringIO(output))
    assert set(frame["Rule ID"]) == {"shared", "mnx", "rhea"}
    shared = frame.set_index("Rule ID").loc["shared"]
    assert shared["RADII"] == "0;1;10"
    assert shared["Score"] == 0.8
    assert shared["EC number"] == "1.1;2.2"
    assert shared["REACTIONS"] == "MNXR1;RHEA:1"
    assert shared["DATASETS"] == "metanetx;rhea"
    assert shared["ECS_COUNT"] == shared["REACTIONS_COUNT"] == 2
    assert shared["RADIUS_MIN"] == 0
    assert shared["RADIUS_MAX"] == 10
    assert pd.read_csv(StringIO(filtered))["Rule ID"].tolist() == ["shared"]
    filtered_row = pd.read_csv(StringIO(filtered), dtype={"RADII": str}).iloc[0]
    assert filtered_row["RADII"] == "10"
    assert filtered_row["RADIUS_MIN"] == filtered_row["RADIUS_MAX"] == 10
    assert [source.read_bytes() for source in sources] == originals


def test_all_is_discovered_and_can_be_reused_offline(tmp_path):
    names = ["metanetx", "rhea", "uspto"]
    for name in names:
        cache_dataset(tmp_path, "3.1.0", name, [(name, "[C]>>[O]", "0", 0.5, "", name)])
    page = "".join(
        f'<a href="/dl/v3.1.0/{name}/templates?format=csv">CSV</a>' for name in names
    ).encode()
    with patch("rrparser.Downloads.urlopen", return_value=BytesIO(page)) as request:
        result = parse_rules(None, rules_dir=str(tmp_path), dataset="all")
        request.assert_called_once()
    assert set(pd.read_csv(StringIO(result))["Rule ID"]) == set(names)
    with patch(
        "rrparser.Downloads.urlopen", side_effect=AssertionError("Network used")
    ):
        assert parse_rules(None, rules_dir=str(tmp_path), dataset="all") == result


def test_latest_aggregation_uses_one_common_release(tmp_path):
    for name in ["metanetx", "rhea"]:
        cache_dataset(tmp_path, "3.0", name, [(name, "[C]>>[O]", "0", 0.5, "", name)])
    page = b"""<a href="/dl/v3.1.0/rhea/templates?format=csv">CSV</a>
    <a href="/dl/v3.0/rhea/templates?format=csv">CSV</a>
    <a href="/dl/v3.0/metanetx/templates?format=csv">CSV</a>"""
    with patch("rrparser.Downloads.urlopen", return_value=BytesIO(page)):
        files = fetch_datasets(tmp_path, "latest", "metanetx,rhea")
    assert all("3.0" in filename for filename in files)
    with patch(
        "rrparser.Downloads.urlopen", side_effect=AssertionError("Network used")
    ):
        assert fetch_datasets(tmp_path, "latest", "rhea+metanetx") == files


@pytest.mark.parametrize("selection", ["all,rhea", "metanetx,", "../rhea"])
def test_invalid_selections(selection, tmp_path):
    with pytest.raises(ValueError):
        fetch_datasets(tmp_path, dataset=selection)


def test_conflicting_templates_are_rejected(tmp_path):
    for name, template in [("metanetx", "[C]>>[O]"), ("rhea", "[O]>>[C]")]:
        cache_dataset(tmp_path, "3.1.0", name, [("same", template, "1", 1, "", name)])
    with pytest.raises(ValueError, match="Conflicting SMARTS"):
        parse_rules(None, rules_dir=str(tmp_path), dataset="metanetx,rhea")


def test_unknown_dataset_is_rejected_before_downloading(tmp_path):
    page = b'<a href="/dl/v3.1.0/rhea/templates?format=csv">CSV</a>'
    with patch("rrparser.Downloads.urlopen", return_value=BytesIO(page)) as request:
        with pytest.raises(ValueError, match="Available releases"):
            fetch_datasets(tmp_path, "3.1.0", "rhea,unknown")
        request.assert_called_once()
    assert not list(tmp_path.iterdir())


def test_merged_score_replacement_and_missing_annotations(tmp_path):
    cache_dataset(
        tmp_path, "3.1.0", "rhea", [("shared", "[C]>>[O]", "0", 0.8, "1.1", "RHEA:1")]
    )
    cache_dataset(
        tmp_path, "3.1.0", "uspto", [("shared", "[C]>>[O]", "10", None, "", "USPTO:1")]
    )
    scores = tmp_path / "scores.csv"
    scores.write_text("Rule ID,Score\nshared,0.9\n")
    result = parse_rules(
        None,
        rules_dir=str(tmp_path),
        dataset="rhea,uspto",
        radii=parse_radii("10"),
        scores_file=str(scores),
    )
    shared = pd.read_csv(StringIO(result)).iloc[0]
    assert shared["Score"] == 0.9
    assert shared["DATASETS"] == "rhea;uspto"
    assert shared["EC number"] == 1.1
