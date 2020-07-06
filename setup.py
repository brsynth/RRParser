from setuptools import setup

with open("README.md", 'r') as fh:
    long_description = fh.read()

required=[
   'requests==2.24.0'
]

with open('RELEASE.md', 'r') as f:
    _version = f.readline().split()[0]

additional_files=[
    ('release', ['RELEASE.md'])
]

setup(
    name="rrparser",
    version=_version,
    author="Thomas Duigou, Melchior du Lac, Joan Hérisson",
    author_email="joan.herisson@univ-evry.fr",
    description="Reaction Rules Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brsynth/RRulesParser",
    packages=['rrparser'],
    package_dir={'rrparser': 'rrparser'},
    install_requires=required,
    include_package_data=True,
    test_suite='discover_tests',
    scripts=['bin/rrparser'],
    data_files=additional_files,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
