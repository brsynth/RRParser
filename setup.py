from setuptools import setup


with open("README.md", 'r') as fh:
    long_description = fh.read()

required=[
   'requests==2.24.0'
]

setup(
    name="rrparser",
    version="1.0.0",
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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
