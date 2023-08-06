django-thjodskra
================

django-thjodskra is a simple app for integrating the icelandic national registry into your project.
You still need to aquire the data files through the proper channel. This project only contains django models and functions for dealing with the archaic fileformat provided by the registry distributors.

###Installation:
pip install django-thjodskra

###Usage:
thjodskra.models.Person corresponds to rows in the national registry.

python manage.py update_people [filename]  
Imports people that have not yet been added to local database and updates the info of those who have.

This can then be added to any script or cronjob as needed.
