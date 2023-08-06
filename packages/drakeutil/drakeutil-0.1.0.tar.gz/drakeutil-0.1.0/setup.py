# -*- coding: utf-8 -*-
#
#  setup.py
#  drakeutil
#

"""
Packaging for drakeutil module.
"""

from setuptools import setup

VERSION = '0.1.0'

requires = [
        'python-datetime-tz>=0.2',
        'python-dateutil>=1.5',
        'pytz>=2012j',
    ]

setup(
        name='drakeutil',
        description="Python helpers for the drake workflow language",
        long_description=open('README.rst').read(),
        url="http://bitbucket.org/larsyencken/drakeutil/",
        version=VERSION,
        author="Lars Yencken",
        author_email="lars@yencken.org",
        license="ISC",
        packages=[
            'drakeutil',
        ],
        install_requires=requires,
        extras_require={
                'mysql': ['MySQL-python>=1.2.3'],
            }
    )
