# RRulesParser

Parser for reaction rules. If no input reaction files is provided, retrieves the reaction rules from [RetroRules](https://retrorules.org/).

## Input

* **rule_type**: (string) Valid options: retro, forward, all. Return the rules that are in reverse, forward or both direction
* **out_folder**: (string) Specify the path where output files will be written
* **diameters**: (integer list): Valid options: 2, 4, 6, 8, 10, 12, 14, 16. The diameter of the rules to return

## Ouput

* **output**: (string): Path of the output file. Either a compressed TAR (containing a CSV) or CSV list of reaction rules that are in a RetroPath2.0 friendly format


## Install
### From pip
```sh
[sudo] python -m pip install rr_parser
```
### From Conda
```sh
[sudo] conda install -c synbiocad rr_parser
```


## Authors

* **Thomas Duigou**
* Melchior du Lac
* Joan Hérisson

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### How to cite RetroRules?
Please cite:

Duigou, Thomas, et al. "RetroRules: a database of reaction rules for engineering biology." Nucleic acids research 47.D1 (2019): D1229-D1235.
