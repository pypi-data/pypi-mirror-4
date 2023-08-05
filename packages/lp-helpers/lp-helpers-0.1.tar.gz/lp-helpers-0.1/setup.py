#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "lp-helpers",
    version = '0.1',
    author = "Brendan Donegan",
    author_email = "brendan-donegan@canonical.com",
    license = "GPL",
    description = "Helper scripts for working with Launchpad and Bazaar.",
    long_description = """
This project provides scripts for simplifying common workflows involving Launchpad and Bazaar
""",
    scripts = ["lp-propose-merge"]
)

