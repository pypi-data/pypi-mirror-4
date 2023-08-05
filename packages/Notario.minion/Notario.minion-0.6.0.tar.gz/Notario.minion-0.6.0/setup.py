#! /usr/bin/python

import os
import glob
from setuptools import setup, find_packages

from ntr import VERSION

description = "A command-line utility to manage notes."

cur_dir = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(cur_dir, 'README')).read()
except:
    long_description = description

datadir = os.path.join(cur_dir, 'data', 'config')
datafiles = [(datadir, [f for f in glob.glob(os.path.join(datadir, '*'))])]

setup(
    name="Notario.minion",
    version=VERSION,
    description=description,
    long_description=long_description,
    url='https://github.com/goliatone/notario',
    license='MIT',
    author='goliatone',
    author_email='hello@goliatone.com',
    keywords='command-line utils notes',
    packages=find_packages(exclude=['experimental']),
    data_files=datafiles,
    install_requires=['setuptools', 'cement'],
    entry_points="""
    [console_scripts]
    ntr = ntr.cli.main:run
    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    # test_suite='nose.collector',
    test_suite='tests'
)
