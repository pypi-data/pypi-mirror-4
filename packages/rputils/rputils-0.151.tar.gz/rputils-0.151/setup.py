#!/usr/bin/env python
# Written by: DGC

# python imports

# local imports
from setuptools import setup

with open("README", "r") as readme_file:
    readme = readme_file.read()

# not strictly a good idea as it uses revision number to identify a changeset
with open(".hg/cache/branchheads", "r") as mercurial_file:
    first_line = mercurial_file.readline()
    mercurial_revision = first_line.split()[1]

setup(
    name="rputils",
    version="0." + mercurial_revision,
    author="David Corne",
    author_email="davidcorne@gmail.com",
    url="https://bitbucket.org/davidcorne/roleplay-utility",
    license="GPLv3",
    description="An application for dice rolling and reading PDF files.",
    long_description=readme,
    packages=["rputils", "rputils.Resources"],
    keywords="rputils roleplay dice pdf random",
    install_requires=["PyQt"],
    platforms=[],
    scripts=["scripts/rputils"],
    classifiers=[
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Topic :: Multimedia :: Graphics :: Presentation",
        ],
    )
