# rrparser
Reaction Rules Parser
| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-rrparser-green.svg)](https://anaconda.org/conda-forge/rrparser) | [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/rrparser.svg)](https://anaconda.org/conda-forge/rrparser) | [![Conda Version](https://img.shields.io/conda/vn/conda-forge/rrparser.svg)](https://anaconda.org/conda-forge/rrparser) | [![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/rrparser.svg)](https://anaconda.org/conda-forge/rrparser) | 

[![Qodana](https://github.com/brsynth/RRParser/actions/workflows/code_quality.yml/badge.svg)](https://github.com/brsynth/RRParser/actions/workflows/code_quality.yml) [![Tests](https://github.com/brsynth/RRParser/actions/workflows/test.yml/badge.svg)](https://github.com/brsynth/RRParser/actions/workflows/test.yml)

## Description

Reaction Rules Parser downloads and caches RetroRules datasets, then writes an
extraction filtered by diameter/radius, rule usage, or EC number. Existing local
CSV/TSV rule files can also be parsed, and rule scores can be replaced.

The default source is **RetroRules 3.1.0 / MetaNetX**, with all even diameters
from **0 to 20** (radii **0 to 10**). The historical **rr02** release remains
available for RetroPath 2.0 workflows.

## Install

```sh
conda install -c conda-forge rrparser
```

## Command line

### Discover and select rules

```sh
# List available release/dataset pairs, including rr02 / metanetx.
python -m rrparser --list-releases

# Use the default release and dataset, including all diameters.
python -m rrparser -o rules.csv

# Extract Rhea templates with diameters 0, 2, 4, 6 and 8.
python -m rrparser --release 3.1.0 --dataset rhea --diameters 0-8 -o rules.csv

# Equivalent selection using radii.
python -m rrparser --dataset rhea --radii 0,1,2,3,4 -o rules.csv

# Historical rr02 rules, restricted to retro usage and diameter 10.
python -m rrparser --release rr02 --rule-type retro -d 10 -o rules.csv

# Parse an existing local rule file.
python -m rrparser --rules_file input.csv -d 2,4 -o rules.csv
```

New releases and their datasets are discovered from the
[RetroRules download page](https://retrorules.org/download), rather than a
hardcoded version list. Available template datasets include `metanetx`, `rhea`
and `uspto`; rr02 supports only `metanetx`. An invalid or unavailable release
reports an error followed by the available release/dataset choices. If the site
is unreachable, the error explains that the list could not be retrieved.

`--release latest` explicitly selects the newest template release for the
chosen dataset; it does not select rr02. Once downloaded, that selection is
reused from cache, including offline. To update, list available releases and
choose a version explicitly, or delete `retrorules-latest-<dataset>.txt` from
the cache to resolve `latest` again. The default remains pinned to `3.1.0`.

### Diameter and radius selection

`--diameters` accepts comma-separated values, inclusive ranges, and comparisons:

| Expression | Selected diameters |
| --- | --- |
| `0,4,8` | 0, 4, 8 |
| `0-8` | 0, 2, 4, 6, 8 |
| `<8` | 0, 2, 4, 6 |
| `<=8` | 0, 2, 4, 6, 8 |
| `>8` | 10, 12, 14, 16, 18, 20 |
| `>=8` | 8, 10, 12, 14, 16, 18, 20 |
| `0-4,18,20` | 0, 2, 4, 18, 20 |

Ranges and comparisons select even values within 0–20. Comma-separated terms
are combined as a union, with duplicates removed. Quote comparisons in the
shell so `<` and `>` are not interpreted as file redirection:

```sh
python -m rrparser --dataset rhea --diameters '<=8' -o rules.csv
python -m rrparser --dataset rhea --diameters '>=8' -o rules.csv
```

Alternatively, `--radii` accepts comma-separated integers from 0 to 10:
`--radii 0,1,2` is equivalent to `--diameters 0,2,4`. The two options are
mutually exclusive. Without either option, all diameters 0,2,…,20 are selected.

For templates, a row is retained when at least one source radius matches
`diameter / 2`, once per template. The output `RADII` column retains all source
radii, separated by semicolons. Explicit odd diameters or values above 20 are
rejected for templates.

rr02 supplies diameters 2,4,…,16. The extended default therefore selects all
its rules. A selection containing no available diameter, such as `-d 20`,
produces a header-only output after the source has been downloaded or loaded.

### Source cache and output

The default cache is **`rrparser/cache/` inside the installed package**, shared
by calls using the same installation. Override it with `--cache-dir` or its
alias `--rules-dir`:

```sh
python -m rrparser --dataset rhea --cache-dir ./cache -d 0-8 -o rules.csv
```

The cache stores complete, original downloads:

- Template releases: `retrorules-<release>-<dataset>.csv.gz`, for example
  `retrorules-3.1.0-rhea.csv.gz`.
- rr02: `retrorules_rr02_rp2_hs.tar.gz`, from the
  [historical Zenodo archive](https://zenodo.org/record/5828017/files/retrorules_rr02_rp2_hs.tar.gz).
  RRParser reads `retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_all.csv`
  directly inside the archive without extracting it to disk.

`-o rules.csv` writes the filtered extraction at the requested location;
filters do not modify the cached source. Changing filters reuses the same
archive without another download. Downloads use a temporary `.part` file,
renamed after completion. The initial rr02 download can take time and currently
has no progress indicator.

If only an old decompressed rr02 CSV cache exists, the original `.tar.gz` is
downloaded once and subsequently reused. That old CSV is not used by the new
archive cache.

### Options

| Option | Purpose / default |
| --- | --- |
| `--rules_file` | Local input file, or `retrorules` (default) to use a cached/downloaded dataset. |
| `--release` | Version, `rr02`, or `latest`; default `3.1.0`. |
| `--dataset` | Dataset name; default `metanetx`. See `--list-releases`. |
| `--list-releases` | Print available release/dataset pairs and exit. |
| `--cache-dir`, `--rules-dir` | Source cache directory; default package-local `rrparser/cache`. |
| `-d`, `--diameters` | List, range, or comparison; default all even diameters 0–20. |
| `--radii` | Comma-separated radii 0–10, as an alternative to `--diameters`. |
| `-rt`, `--rule-type` | `all` (default), `retro`, or `forward`; templates require `all`. |
| `-ec`, `--ec` | File of comma-separated EC prefixes to keep. |
| `-ecx`, `--ecx` | File of comma-separated EC prefixes to exclude; mutually exclusive with `--ec`. |
| `-s`, `--scores` | CSV/TSV file with `Rule ID` and `Score` columns to replace matching scores. |
| `-if`, `--input-format` | Local input format: `csv` (default) or `tsv`. Downloaded rules are CSV. |
| `-of`, `--output-format` | Output format: `csv` (default) or `tsv`. |
| `-o`, `--outfile` | Extraction destination; `.gz` outputs are compressed. Without a destination, results are printed to the console. |
| `--log` | Logging level; default `info`. |
| `--version` | Print RRParser's version and exit. |

Run `python -m rrparser --help` for the full CLI help.

## Python API

Use keyword arguments to select the source, filters and output:

```python
from rrparser import list_retrorules, parse_rules

# Mapping: (release, dataset) -> download URL.
choices = list_retrorules()

# Write an extraction. Returns None when outfile is provided.
parse_rules(
    outfile='rules.csv',
    release='3.1.0',
    dataset='rhea',
    diameters='<=8',
)

# Return CSV text instead of writing a file.
csv_text = parse_rules(
    outfile=None,
    dataset='rhea',
    radii='0,1,2',
)

# Parse a local file with EC filtering and replacement scores.
parse_rules(
    outfile='filtered.csv',
    rules_file='input.csv',
    diameters='2,4',
    ec=['1.1'],
    scores_file='scores.csv',
)
```

`rules_dir=` overrides the cache directory. `release=`, `dataset=`, and cache
lookup apply when `rules_file='retrorules'`, the default. Diameter expressions
have the same meaning in Python and on the CLI. Pass `radii=` as an alternative
to `diameters=`. `ec=` and `ecx=` take lists of prefixes; `read_ecnumbers()`
can load these from a comma-separated file. Invalid selections raise
`ValueError`; the CLI reports these errors and exits with status 1.

The CLI argument parser is also available:

```python
from rrparser import build_args_parser

parser = build_args_parser()
params = parser.parse_args(['--dataset', 'rhea', '--diameters', '<=8'])
```

## Output compatibility

New templates use implicit hydrogens and have a different schema from rr02's
RetroPath 2.0 rules with explicit hydrogens. RRParser renames these columns:

| Template source column | Output column |
| --- | --- |
| `TEMPLATE_ID` | `Rule ID` |
| `TEMPLATE` | `Rule` |
| `ECS` | `EC number` |
| `SCORE` | `Score` |

Other source columns, including `REACTIONS`, `RADII`, `RADIUS_MIN`,
`RADIUS_MAX`, and `DATASETS`, are retained. Templates do not provide
retro/forward annotations, so they require `rule_type='all'`. EC filtering and
replacement scores remain supported. rr02 retains its historical output
schema and rule usage filters. Existing local RetroPath CSV/TSV files remain
supported through `--rules_file` or `rules_file=`.

## Tests

Run all tests:

```sh
python -m pytest -v
```

Tests use local fixtures, small in-memory archives, and mocked network
responses; no live download is required. They cover discovery, version errors,
cache reuse, original rr02 archive preservation, extraction, diameter/radius
filtering, score replacement, and rr02 retro/forward filters.
CI workflows are available in [`.github/workflows`](.github/workflows).

## Authors

* **Joan Hérisson**
* Melchior du Lac
* Thomas Duigou

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### How to cite RetroRules?
Please cite:

Duigou, Thomas, et al. "RetroRules: a database of reaction rules for engineering biology." Nucleic acids research 47.D1 (2019): D1229-D1235.
