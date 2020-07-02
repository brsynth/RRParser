import setuptools

from glob import glob
from os import remove, path
from setuptools import setup


with open("README.md", 'r') as fh:
    long_description = fh.read()

with open("rr_parser/requirements.txt", 'r') as f:
    required = f.read().splitlines()

setup(
    name="rr_parser",
    version="1.0.4",
    author="Thomas Duigou, Melchior du Lac, Joan Hérisson",
    author_email="joan.herisson@univ-evry.fr",
    description="RRulesParser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brsynth/RetroRules",
    packages=['rr_parser'],
    package_dir={'rr_parser': 'rr_parser'},
    install_requires=required,
    include_package_data=True,
    test_suite = 'discover_tests',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
