#!/usr/bin/env python
"""
Election data parser 
====

An incomplete collection of libraries and tools to processs
election data.

"""

from setuptools import setup
from glob import glob
import election_parser

setup(
    name='election_parser',
    version="%d.%d.%d" % election_parser.VERSION,
    url="http://github.com/adamdeprince/election_parser",
    author = "Adam DePrince",
    author_email = "deprince@googlealumni.com",
    description="Parse US real time and archived election data.  Really only supports CA real time rigth now",
    long_description=__doc__,
    packages = ["election_parser","election_parser.test"],
    package_data = {'':['*.zip']},
    # zip_safe=True,
    license='GPLv2',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        ],
    scripts = [
        "scripts/fake_election_server",
        "scripts/fetch_parse_and_upload_election_data", 
        ],
    install_requires = [
        'paramiko',
        'python-gflags',
        'pycurl',
        'scpclient',
        'unittest2'
        ]
)
