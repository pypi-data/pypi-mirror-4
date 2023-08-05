#!/usr/bin/env python

import os
import shutil
from setuptools import setup, find_packages

def read(fname):
    return "\n" + open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Xnt",
    version="0.2.0",
    author="Kenny Ballou",
    author_email="kennethmgballou@gmail.com",
    url="https://bitbucket.org/devnulltao/xnt",
    description=("High-Level build script for doing more complex build tasks"),
    packages=find_packages(),
    scripts=["xnt/xenant.py",],
    package_data={
    },
    long_description=read("README"),
    platforms=["Linux", "Windows",],
    entry_points={
        'console_scripts': [
            'xnt = xnt.xenant:main',
        ],
    },
    install_requires=['distribute',],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
    ],
)
