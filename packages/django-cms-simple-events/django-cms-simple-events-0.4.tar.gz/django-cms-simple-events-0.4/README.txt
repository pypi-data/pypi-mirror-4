=============================
Django CMS Simple Events
============================

Name: django-cms-simple-events
Description: A `Django CMS <http://www.django-cms.org/>`_ application for managing an events calendar.
Download: https://bitbucket.org/chucu/django-cms-simple-events


Dependancies
============

- django (tested with 1.5.1)
- django-cms (tested with 2.4)
- django-hvad


Installation
============

Download
--------

From PyPI
'''''''''

You can simply type into a terminal ``pip install django-cms-simple-events`` or ``easy_install django-cms-simple-events``.

Manually
''''''''

You can download from https://bitbucket.org/chucu/django-cms-simple-events.

Unzip the file you downloaded. Then go in your terminal and ``cd`` into the unpacked folder. 
Then type ``python setup.py install`` in your terminal.

Setup
-----

Put ``'simple_events'`` in your ``INSTALLED_APPS`` section in settings.py. 
Don't forget to syncdb your database or migrate if you're using South.

Example:

INSTALLED_APPS = ( 
    ...
    'hvad',
    'simple_events',
)
