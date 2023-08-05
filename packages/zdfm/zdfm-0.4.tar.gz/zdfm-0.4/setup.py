#!/usr/bin/env python3

from setuptools import setup

setup(name="zdfm",
      version="0.4",
      description="Downloader for the ZDF Mediathek",
      author="Marian Beermann",
      author_email="public@enkore.de",
      license="MIT",

      py_modules=["zdfm"],
      entry_points={
          "console_scripts": ["zdfm = zdfm:main"],
      },
      install_requires=[
        "lxml",
      ]
     )
