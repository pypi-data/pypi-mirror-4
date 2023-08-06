django-staticfiles-moment
=========================
Moment.js meets Django staticfiles


Usage
-----
This application is meant to be used with `django-staticfiles`_.  Make sure
that staticfiles setup and configured, then install this application using
`pip`_:

::

	pip install django-staticfiles-moment

Finally, make sure that `moment` is listed in your ``INSTALLED_APPS``.  You
can use this oneliner to add it as well:

::

	INSTALLED_APPS += ['moment', ]


Build
-----
`Moment.js`_ ships with a pre-built version in each tag.  No build step is
required, so there are no additional requirements other than running ``python
support/build.py``.


.. _django-staticfiles: https://github.com/jezdez/django-staticfiles
.. _pip: http://www.pip-installer.org/
.. _Moment.js: http://momentjs.com/
