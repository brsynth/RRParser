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
* **diameters**: (integer list) Valid options: 2, 4, 6, 8, 10, 12, 14, 16. The diameter of the rules to return
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
  diameters=<'2,4,6,8,10,12,14,16'>,
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
  [--diameters {2,4,6,8,10,12,14,16}] \
  [--output-format {csv,tsv}]
```
If `rules_files` is set to `retrorules`, RetroRules are fetched from `retrorules.org` and considered as input file.

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
