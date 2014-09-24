#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
	name = "Clotho",
	version = "0.1.2",
	install_requires = ["scikit-learn", "beautifulsoup4", "nltk", "requests", "wget", "rdflib", "wikipedia", "SPARQLWrapper", "MySQL-python", "numpy>=1.9", "scipy>=0.14", "matplotlib>=1.4"]
)


"""
packages = find_packages(),
scripts = [],
"""