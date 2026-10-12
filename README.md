# rrparser
Reaction Rules Parser
| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-rrparser-green.svg)](https://anaconda.org/conda-forge/rrparser) | [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/rrparser.svg)](https://anaconda.org/conda-forge/rrparser) | [![Conda Version](https://img.shields.io/conda/vn/conda-forge/rrparser.svg)](https://anaconda.org/conda-forge/rrparser) | [![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/rrparser.svg)](https://anaconda.org/conda-forge/rrparser) | 

[![Qodana](https://github.com/brsynth/RRParser/actions/workflows/code_quality.yml/badge.svg)](https://github.com/brsynth/RRParser/actions/workflows/code_quality.yml) [![Tests](https://github.com/brsynth/RRParser/actions/workflows/test.yml/badge.svg)](https://github.com/brsynth/RRParser/actions/workflows/test.yml)

## Description
*Reaction Rules Parser*. If no input reaction files is provided, retrieves the reaction rules from [RetroRules](https://retrorules.org).

## Input

* **rules-file**: (string) Filename of reaction rules
* **outfile**: (string) Filename containing the result of the parsing. If not set, result is printed out in the console. If ends with '.gz', it will be gzipped.
* **input-format**: (string) Valid options: csv, tsv. Format of the input file
* **rule-type**: (string) Valid options: retro, forward, all. Return the rules that are in reverse, forward or both direction
* **diameters**: (integer list) Even values from 0 to 20 (all by default). For templates, diameter = 2 × radius; rr02 provides diameters 2 to 16.
* **output-format**: (string) Valid options: csv, tar.gz. Format of the returned file


## Install
### From Conda
```sh
[sudo] conda install -c conda-forge rrparser
```

## Use

### Function call from Python code
```python
from rrparser import parse_rules

outfile = parse_rules(
  <rules_file>,
  <outfile>,
  input_format=<'csv' | 'tsv'>,
  rule_type=<'all' | 'retro' | 'forward'>,
  diameters=<'0,2,4,6,8,10,12,14,16,18,20'>,
  output_format=<'csv' | 'tsv'>
)
```

If parameters from CLI have to be parsed, the function `build_args_parser` is available:
```python
from rrparser import build_args_parser

parser = buildparser()
params = parser.parse_args()
```

### Run from CLI
```sh
python -m rrparser \
  rules-file <filename> \
  [--input-format {csv,tsv}] \
  [--rule-type {all,retro,forward}] \
  [--outfile <filename>] \
  [--diameters 0,2,4,6,8,10,12,14,16,18,20] \
  [--output-format {csv,tsv}]
```
If `rules_files` is set to `retrorules`, RetroRules are fetched from `retrorules.org` and considered as input file.

### Choose a RetroRules release

```sh
python -m rrparser --list-releases
python -m rrparser --release 3.1.0 --dataset rhea --rules-dir ./rules -o rules.csv
python -m rrparser --dataset rhea --radii 0,1,2 --cache-dir ./cache -o rules.csv
python -m rrparser --release rr02 --rules-dir ./rules --rule-type retro -o rules.csv
```

Versions and datasets are discovered from https://retrorules.org/download.
The list also includes `rr02` / `metanetx`, using the historical
[Zenodo archive](https://zenodo.org/record/5828017/files/retrorules_rr02_rp2_hs.tar.gz)
for RetroPath 2.0 with explicit hydrogens. `--release rr02` reuses the old cache
path when present and supports the original retro/forward filters.
The default is `--release 3.1.0 --dataset metanetx`; explicit `--release latest` selects only
the newer template releases.
Downloaded CSV archives are cached separately by version and dataset. `latest`
reuses its first downloaded version, including offline. Run `--list-releases`
and specify a version to download a newer release; delete the corresponding
`retrorules-latest-<dataset>.txt` cache file to resolve `latest` again.

The default cache is `rrparser/cache` inside the installed package, shared
by calls using that installation. Override it with `--cache-dir` (alias of `--rules-dir`) or `rules_dir=`
in Python. The complete source archive stays in this cache; `-o rules.csv`
writes the filtered extraction in the requested location. Without a size
filter, the extraction includes all radii. Changing diameters or radii reuses
the same archive without downloading it again.

New templates use implicit hydrogens and differ from the old RetroPath rule
schema. RRParser renames `TEMPLATE_ID`, `TEMPLATE`, `ECS`, and `SCORE` to
`Rule ID`, `Rule`, `EC number`, and `Score`, retaining the other source columns.
Diameter filtering selects templates with a matching radius (`diameter / 2`),
once per template. Radii 0–10 correspond to even diameters 0–20, all included
by default. Odd diameters and values above 20 are rejected for templates.
Use `--radii 0,1,2` instead of `--diameters 0,2,4`; these CLI options are
mutually exclusive. Python calls also accept `radii='0,1,2'`.
For rr02, the extended default includes all available diameters (2–16).
`RADII` retains all source radii, separated by semicolons.
EC filtering and custom scores remain available. New templates require
`--rule-type all`, since they do not supply retro/forward annotations.
Existing local RetroPath CSV/TSV files remain supported via `--rules_file`.

In Python, use `list_retrorules()` to discover `(release, dataset)` choices,
and pass `release=` and `dataset=` to `parse_rules()`.

## Tests
Test can be run with the following commands:

### Natively
```bash
python -m pytest -v
```

# CI/CD
For further tests and development tools, a CI toolkit is provided in `ci` folder (see [ci/README.md](ci/README.md)).

## Authors

* **Joan Hérisson**
* Melchior du Lac
* Thomas Duigou

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### How to cite RetroRules?
Please cite:

Duigou, Thomas, et al. "RetroRules: a database of reaction rules for engineering biology." Nucleic acids research 47.D1 (2019): D1229-D1235.
