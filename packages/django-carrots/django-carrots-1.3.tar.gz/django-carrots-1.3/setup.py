# -*- coding: utf8 -*-

from setuptools import setup, find_packages

setup(
    name="django-carrots",
    version="1.3",
    packages=find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['django-social-auth3'],

    #package_data={
    #    '': ['*.html'],
    #},
    package_data = {
        'account': ['templates/account/*.html', 'templates/*.html'],
    },

    # metadata for upload to PyPI
    author=u"Krzysztof Płocharz",
    author_email="krzysztof@plocharz.info",
    description="Basic account application for Django Workshops by Geek Girl Carrots",
    license="PSF",
    keywords="django facebook account",
    url="http://geekgirlscarrots.pl/",
    include_package_data = True,
)
