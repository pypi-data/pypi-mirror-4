#!/usr/bin/env python

from distutils.core import setup

with open("DESCRIPTION.rst") as f:
    long_description = f.read()

setup(
    name="dotty",
    version="0.1.0",
    scripts=["dotty"],
    data_files=[
        ("/etc", ["dottyrc"]),
    ],
    description="Configuration file manager",
    long_description=long_description,
    url="http://scrace.org/software/dotty.html",
    author="Thomas Scrace",
    author_email="tom@scrace.org",
    classifiers=[
        "Programming Language :: Python",
        "License :: Public Domain",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Systems Administration",
    ]
)
