django-staticfiles-select2
==========================
Introducing select2 to Django!


Usage
-----
This application is meant to be used with `django-staticfiles`_.  Make sure
that staticfiles setup and configured, then install this application using
`pip`_:

::

	pip install django-staticfiles-select2

Finally, make sure that `select2` is listed in your ``INSTALLED_APPS``.  You
can use this oneliner to add it as well:

::

	INSTALLED_APPS += ['select2', ]


Inspiration
-----------

Most part of this project are stolen from `django-staticfiles-jquery`_.

.. _django-staticfiles-jquery: https://github.com/tswicegood/django-staticfiles-jquery
.. _django-staticfiles: https://github.com/jezdez/django-staticfiles
.. _pip: http://www.pip-installer.org/
