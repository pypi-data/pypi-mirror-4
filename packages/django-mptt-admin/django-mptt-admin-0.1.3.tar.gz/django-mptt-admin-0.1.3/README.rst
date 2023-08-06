|Travis Status|

|Coverage Status|

Django Mptt Admin
=================

*Django-mptt-admin* provides a nice Django Admin interface for Mptt
models. The source is available on
https://github.com/leukeleu/django-mptt-admin. It uses the
`jqTree <http://mbraak.github.io/jqTree/>`__ library.

.. figure:: https://raw.github.com/leukeleu/django-mptt-admin/master/screenshot.png
   :alt: Screenshot

   Screenshot
Requirements
------------

The package is tested with Django 1.4.5 and 1.5.1, and Mptt 0.5.5. Also
with Python 2.6 and 2.7.

-  This version is not compatible with Django 1.3. Please use
   django-mptt-admin 0.1.2 for Django 1.3 support.

-  There is experimental support for Python 3. This works with Django
   1.5+ and with the *update-things* branch of django-mptt.

Installation
------------

Install the package:

::

    $ pip install django_mptt_admin

Add **django\_mptt\_admin** to your installed apps in **settings.py**.

::

    INSTALLED_APPS = (
        ..
        'django_mptt_admin',
    )

Use the DjangoMpttAdmin class in admin.py:

::

    from django.contrib import admin
    from django_mptt_admin.admin import DjangoMpttAdmin
    from models import Country

    class CountryAdmin(DjangoMpttAdmin):
        pass

    admin.site.register(Country, CountryAdmin)

Changelog
---------

**0.1.3** (development version)

*This version drops support for Django 1.3.7*

-  Issue 2: Posting a screenshot in the readme would be really useful
   (thanks to Andy Baker)
-  Issue 3: Use static templatetag for CDN-compatible file paths (thanks
   to Alex Holmes)
-  Added
   `Coveralls <https://coveralls.io/r/leukeleu/django-mptt-admin>`__
   support

**0.1.2** (march 12 2013)

-  Issue 1: Grid view doesn't link correctly to object change pages
   (thanks to Kris Fields)

**0.1.1** (februari 25 2013)

-  Added experimental Python 3 support

**0.1** (februari 7 2013)

-  Initial version

.. |Travis Status| image:: https://secure.travis-ci.org/leukeleu/django-mptt-admin.png
   :target: http://travis-ci.org/leukeleu/django-mptt-admin
.. |Coverage Status| image:: https://coveralls.io/repos/leukeleu/django-mptt-admin/badge.png?branch=master
   :target: https://coveralls.io/r/leukeleu/django-mptt-admin
