#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="radish-bdd",
    version="0.01.01",
    description="Behaviour-Driven-Development tool for python",
    author="Timo Furrer",
    author_email="tuxtimo@gmail.com",
    url="http://github.com/timofurrer/radish",
    package_dir={"radish.singleton": "radish/pysingleton/singleton"},
    packages=["radish", "radish.Writers", "radish.singleton"],
    entry_points={"console_scripts": ["radish = radish.main:main"]},
    package_data={"radish": ["*.md"]}
)
