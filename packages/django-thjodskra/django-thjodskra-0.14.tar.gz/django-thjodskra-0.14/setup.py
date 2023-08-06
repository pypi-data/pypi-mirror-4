#encoding: utf-8
from distutils.core import setup

setup(
	name = "django-thjodskra",
    version = "0.14",
    description = "django-thjodskra is a simple app for integrating the icelandic national registry into your django project",
    author = "Úlfur Kristjánsson",
    author_email = "ulfur@theawesometastic.com",
    url = "https://github.com/ulfur/django-thjodskra",
    packages = ['thjodskra', 'thjodskra.management', 'thjodskra.management.commands'],
    package_data = {
					'thjodskra' : ["thjodskra/*.py"],
					'management': ["thjodskra/management/*.py"],
					'commands'	: ["thjodskra/management/commands/*.py"]
					},
)