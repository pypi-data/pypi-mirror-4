#!/usr/bin/env python
"""
Utilities to compute election results

"""

from setuptools import setup
import election

setup(
    name='election',
    version="%d.%d.%d" % election.VERSION,
    url="http://github.com/wnyc/election",
    author = "Adam DePrince",
    author_email = "deprince@googlealumni.com",
    long_description=__doc__,
    zip_safe=True,
    license='GPLV3',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        ],
    scripts = [
        ],
    install_requires = [
        ]
)
