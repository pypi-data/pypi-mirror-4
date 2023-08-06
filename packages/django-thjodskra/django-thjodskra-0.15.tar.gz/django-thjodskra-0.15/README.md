django-thjodskra
================

django-thjodskra is a simple app for integrating the icelandic national registry into your project.
You still need to aquire the data files through the proper channel. This project only contains django models and functions for dealing with the archaic fileformat provided by the registry distributors.

###Usage:
manage.py import_users [filename]

manage.py update_users [filename]

These can then be added to any script or cronjob as needed.
