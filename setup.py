from distutils import sys
import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

PACKAGE = "Chern"
NAME = "Chern"
DESCRIPTION = "A data analysis management toolkit for high energy physics"
AUTHOR = "Mingrui Zhao"
AUTHOR_EMAIL = "mingrui.zhao@mail.labz0.org"
URL = "https://github.com/zhaomr13/Chern"
VERSION = __import__(PACKAGE).__version__
here = os.path.dirname(__file__)
setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    url = URL,
    classifiers = [
        'Development Status :: 4 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',

    ],
    zip_safe=False,
    keywords = "Analysis Perservation",
    packages = find_packages(exclude=[]),
    install_requires = [
        "click", "colored", "diff-match-patch", "python-daemon", "ipython", "PyYAML>=5.1,<6.0"
    ],
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'chern4 = Chern.main:main',
            'chern = Chern.main:main'
        ]
    }
)
