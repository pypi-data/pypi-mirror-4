#!/usr/bin/env python

from distutils.core import setup

setup( name = "nanotest",
       version = "2.0.2",
       description = "Tiny testing toolkit (for Python)",
       author = "Shawn Boyette",
       author_email = "shawn@firepear.net",
       url = "https://github.com/firepear/nanotest-py",
       py_modules = ["nanotest"],
       scripts = ['bin/nanotest-py'],
       classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ]
)
