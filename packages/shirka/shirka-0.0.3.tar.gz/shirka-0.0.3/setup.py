#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name="shirka",
    version="0.0.3",
    description="A small bot based on twisted",
    author="Thomas Rabaix",
    author_email="thomas.rabaix@gmail.com",
    url="https://github.com/rande/python-shirka",
    py_modules=["shirka"],
    packages = ['shirka', 'shirka.consumers', 'shirka.responders', 'shirka.control', 'shirka.tools'],
    install_requires=["ioc", "twisted", "twistedhttpstream"],
)