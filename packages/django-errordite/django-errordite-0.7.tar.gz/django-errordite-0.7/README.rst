Django-Errordite
================

This package provides integration between Django and Errordite.

The application is provided in the form of a standard Python logging handler.

It is a django-aware subclass of the errordite package logging handler. This
means that in addition to logging core exception information (which the base
``errordite`` handler will do), this handler is context-aware, and if you pass
a django request object into the logger then relevant information will be
extracted from the request and added to the data sent to Errordite. Additional
information includes: client ip address, user agent, x-forwarded-for header
(in case you are behind a load balancer), django user username (if exists).

In order to append the request to the log record, add it to the ``extra`` arg::

    import logging
    logger = logging.getLogger(__name__)

    def index_view(request):
        """
        Standard django view method.
        """
        try:
            do_something()
        except:
            logger.error("Something went wrong.", extra={'request': request})

See Python docs on logging for more details on the 'extra' keyword arg:
http://docs.python.org/2/library/logging.html#logging.Logger.debug

Installation
------------

The library is available at pypi as 'django-errordite', and can therefore be
installed using pip::
    
    $ pip install django-errordite

Dependencies
------------

This package is dependent on the ``errordite`` package - which should be
installed automatically.

Configuration
-------------

In order to set up a valid **DjangoErrorditeHandler** you must pass in an
Errordite API token, which you can get by signing up at http://www.errordite.com

The logging handler should be configured in the django ``settings.py`` file.

This is an extract from a basic ``settings.py`` that extracts the token from
the local environment, and configures a single logger::

    import os

    ERRORDITE_TOKEN = os.environ.get('ERRORDITE_TOKEN', None)
    if ERRORDITE_TOKEN is None:
        raise Exception("You must set the ERRORDITE_TOKEN environment "
                        "variable if you wish to run the tests.")

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'django_errordite': {
                'level': 'DEBUG',
                'class': 'django_errordite.DjangoErrorditeHandler',
                'token': ERRORDITE_TOKEN,
                'formatter': 'simple'
            },
        },
        'loggers': {
            'test': {
                'handlers': ['django_errordite'],
                'propagate': False,
                'level': 'DEBUG',
            },
        }
    }


Tests
-----

There are tests in the package - they can be run using the django test runner::

    $ cd to/django-errordite/package/directory
    $ python manage.py test test_app

The ``test_app`` is an empty django application that is in the package redist
that is used to force the django test runner to load only the package tests (
i.e. without running the entire django test suite.)

NB These tests do log real exceptions over the wire, so you will need to be
connected to the web to run them. You will also need to set a local environment
variable (**ERRORDITE_TOKEN**), which is picked up in the test suite.

If you are \*nix you can pass this in on the command line::

    $ ERRORDITE_TOKEN=123 python manage.py test test_app

If you are on Windows you'll need to set it up explicitly as an env var::

    c:\> set ERRORDITE_TOKEN=123
    c:\> python manage.py test test_app

(This is a technique used to prevent having to have sensitive information in
the public repo.)
