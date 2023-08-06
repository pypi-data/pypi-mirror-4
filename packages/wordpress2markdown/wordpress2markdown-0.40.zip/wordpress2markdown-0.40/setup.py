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
    name="wordpress2markdown",
    packages = ["wordpress2markdown"],
    version="0." + mercurial_revision,
    author="David Corne",
    author_email="davidcorne@gmail.com",
    url="https://bitbucket.org/davidcorne/wordpress-to-markdown",
    license="GPLv3",
    description="A script to convert wordpress.com html into markdown.",
    long_description=readme,
    keywords="wordpress html markdown convert utility",
    platforms=[],
    scripts=["scripts/wordpress2markdown"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
    )
