import os.path
from setuptools import setup, find_packages

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name = "localwiki-geocode-pagenames",
    version = "0.1.1",
    description = "A script to semi-automatically map pages in a LocalWiki instance",
    long_description = open(os.path.join(base_dir, "README")).read(),
    url = "https://github.com/philipn/localwiki_geocode_pagenames",
    author = "Philip Neustrom",
    author_email = "philipn@gmail.com",
    packages = find_packages(),
    zip_safe = False,
    scripts = ['localwiki-geocode-pagenames'],
    install_requires = [
        'slumber',
        'geopy',
    ],
)
