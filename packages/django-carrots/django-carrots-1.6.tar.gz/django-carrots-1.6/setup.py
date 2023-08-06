# -*- coding: utf8 -*-
import re
import os
import sys

from setuptools import setup, find_packages

setup(
    name="django-carrots",
    version="1.6",
    packages=find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['django-social-auth3'],

    # metadata for upload to PyPI
    author=u"Krzysztof Płocharz",
    author_email="krzysztof@plocharz.info",
    description="Basic account application for Django Workshops by Geek Girl Carrots",
    license="PSF",
    keywords="django facebook account",
    url="http://geekgirlscarrots.pl/",
    include_package_data = True,
)
