from setuptools import setup

with open(".env", 'r') as f:
    for line in f:
        if line.startswith('PACKAGE'):
            _package = line.splitlines()[0].split('=')[1]
            break

with open("README.md", 'r') as f:
    long_description = f.read()

required=[
   'requests==2.24.0'
]

extra_files={
    'release': [_package+'/RELEASE.md']
}

with open(extra_files['release'][0], 'r') as f:
    _version = f.readline().split()[0]


setup(
    name=_package,
    version=_version,
    author="Thomas Duigou, Melchior du Lac, Joan Hérisson",
    author_email="joan.herisson@univ-evry.fr",
    description="Reaction Rules Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brsynth/RRulesParser",
    packages=[_package],
    package_dir={_package: _package},
    install_requires=required,
    include_package_data=True,
    test_suite='discover_tests',
    data_files=[(k, v) for k, v in extra_files.items()],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
