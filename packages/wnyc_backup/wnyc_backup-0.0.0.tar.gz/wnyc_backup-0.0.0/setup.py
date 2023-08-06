#!/usr/bin/env python
"""
wnyc_backup
===========

WNYC's backup utility
"""

from setuptools import setup

setup(
    name = 'wnyc_backup',
    version = '0.0.0',
    author = 'Adam DePrince',
    author_email = 'adeprince@nypublicradio.org',
    description='Simple staggered backups',
    long_description=__doc__,
    py_modules = ["wnyc_backup"],
    packages=["wnyc_backup"],
    zip_safe=True,
    license="GPL",
    include_package_data=True,
    url = "http://github.com/wnyc/wnyc_backup",
    install_requires = [
        "boto",
        "python-cloudfiles",
        "python-gflags",
        "unittest2",
        ],
    scripts = [
        "scripts/wnyc_backup_cull",
        "scripts/wnyc_backup_upload",
        ]
)


