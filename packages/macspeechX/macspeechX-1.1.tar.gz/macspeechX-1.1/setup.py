#!/usr/bin/env python
"""
Setup file for macspeechX using distutils package.

"""
import os

from distutils.core import setup,Extension

rev="$Revision: 1.1 $"

#
setup(name="macspeechX",
      version="1.1",
      author="Noboru Yamamoto, KEK, JAPAN",
      author_email = "Noboru.YAMAMOTO_at_kek.jp",
      url="http://www-acc.kek.jp/",
      py_modules=["macspeechX"]
      )
