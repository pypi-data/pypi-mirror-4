#!/usr/bin/env python

import os
import shutil

from distutils.core import setup

if not os.path.exists("README.txt"):
    shutil.copy("README.md", "README.txt")

setup(name='gnucashxml',
      version='1.0',
      description="Parse GNU Cash XML files",
      author="Jorgen Schaefer",
      author_email="forcer@forcix.cx",
      url="https://github.com/jorgenschaefer/gnucashxml",
      py_modules=['gnucashxml']
      )
