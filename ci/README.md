# CI toolkit

This Continuous Integration toolkit provides tools to build and publish Conda packages. It is also possible to run fast tests in order to debug code.

## Requirements
* [conda](https://docs.conda.io)
* [make](https://www.gnu.org/software/make)

Requirements can be provided by a docker container by running the following commands (at package root folder):
```bash
docker run -it --rm -v $PWD:$PWD -w $PWD continuumio/anaconda3 bash
conda update --all -y
apt-get update
apt-get install -y make
cd ci
```

## Conda workflow

### Build
The building stage of conda package can be performed by:
```bash
make build [python=<ver>]
```
Equivalent to `conda build --build-only`. Only run the build, without  any  post  processing  or  testing. For tests, please see section about Test stage.

If `python` option is set then this stage is only performed for the version `<ver>` of Python. By default, the Python version will be the latest available within the building environment.

### Test
The testing stage of conda package can be performed by:
```bash
make test [python=<ver>] [env=<conda_env_name>]
```
Equivalent to `conda build --test`.

If `python` option is set then this stage is only performed for the version `<ver>` of Python. By default, the Python version will be the latest available within the building environment.

### Convert
The converting stage of conda package can be performed by:
```bash
make convert [python=<ver>] [env=<conda_env_name>]
```
Equivalent to `conda convert`, the conversion is performed for all plaforms (`linux-64`, `osx-64` and `win-64`).

If `python` option is set then this stage is only performed for the version `<ver>` of Python. By default, the Python version will be the latest available within the building environment.

### Publish
The publishing stage of conda package can be performed by:
```bash
make publish [python=<ver>] [env=<conda_env_name>]
```
Equivalent to `anaconda upload`.

If `python` option is set then this stage is only performed for the version `<ver>` of Python. By default, the Python version will be the latest available within the building environment.
Credentials have to be stored in `.secrets` file with the following syntax:
```
ANACONDA_USER=<username>
ANACONDA_TOKEN=<token>
```

## Development tools
Conda workflow is heavy and long to perform. For development or debugging purposes, fast testing process is possible by:
```bash
make f-test [env=<conda_env_name>]
```
Equivalent to `pytest`, this stage is achieved within a conda environment.

If `env` option is set then this stage is performed in `<conda_env_name>` (default: `test`) conda environment.

Requirements can be provided by a docker container. It could the same than Conda workflow uses (`continuumio/anaconda3`). Nevertheless, a lighter image can be used by running the following commands (at package root folder):
```bash
docker run -it --rm -v $PWD:$PWD -w $PWD continuumio/miniconda3 bash
conda update --all -y
apt-get update
apt-get install -y make
cd ci
```


## Authors

* **Joan Hérisson**

## Acknowledgments

* Thomas Duigou


## Licence
CI toolkit is released under the MIT licence. See the LICENCE file for details.
