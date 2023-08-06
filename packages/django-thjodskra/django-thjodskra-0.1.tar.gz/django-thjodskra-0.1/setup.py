#encoding: utf-8

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "django-thjodskra",
    version = "0.1",
    packages = find_packages(),
    author = "Úlfur Kristjánsson",
    author_email = "ulfur@theawesometastic.com",
    description = "A package for integrating the icelandic national registry into your Django project.",
    url = "https://github.com/ulfur/django-thjodskra",
    include_package_data = True
)