#encoding: utf-8
from distutils.core import setup

files = ["thjodskra/*.py","thjodskra/management/*.py","thjodskra/management/commands/*.py"]

setup(
	name = "django-thjodskra",
    version = "0.13",
    description = "django-thjodskra is a simple app for integrating the icelandic national registry into your django project",
    author = "Úlfur Kristjánsson",
    author_email = "ulfur@theawesometastic.com",
    url = "https://github.com/ulfur/django-thjodskra",
    packages = ['thjodskra'],
    package_data = {'thjodskra' : files },
)