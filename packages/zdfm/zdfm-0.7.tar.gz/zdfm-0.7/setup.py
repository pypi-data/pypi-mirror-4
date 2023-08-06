#!/usr/bin/env python3

from setuptools import setup

setup(name="zdfm",
      version="0.7",
      description="Downloader for the ZDF Mediathek",
      url="http://github.com/enkore/zdfm/",
      author="Marian Beermann",
      author_email="public@enkore.de",
      license="MIT",

      py_modules=["zdfm"],
      entry_points={
          "console_scripts": ["zdfm = zdfm:main"],
      },
     )
