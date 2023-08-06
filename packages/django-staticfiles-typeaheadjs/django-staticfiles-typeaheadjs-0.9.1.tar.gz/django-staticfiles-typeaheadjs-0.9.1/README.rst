django-staticfiles-typeaheadjs
==============================
typeahead.js meets Django staticfiles


Usage
-----
This application is meant to be used with `django-staticfiles`_.  Make sure
that staticfiles setup and configured, then install this application using
`pip`_:

::

	pip install django-staticfiles-typeaheadjs

Finally, make sure that `typeaheadjs` is listed in your ``INSTALLED_APPS``.  You
can use this oneliner to add it as well:

::

	INSTALLED_APPS += ['typeaheadjs', ]


Build
-----
`typeahead.js`_ uses `Grunt`_ to build and minify the JavaScript.  You need to
follow the instructions in ``vendor/typeahead.js/README.md`` for setting up your
build environment, then run ``python support/build.py`` to update the Django
application.  See ``support/build.py`` for more information on how data is
transferred from the submodule to the Python package.


.. _django-staticfiles: https://github.com/jezdez/django-staticfiles
.. _pip: http://www.pip-installer.org/
.. _typeahead.js: http://twitter.github.com/typeahead.js/
.. _Grunt: http://gruntjs.com/
