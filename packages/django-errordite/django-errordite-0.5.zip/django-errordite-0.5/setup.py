"""
Setup file for django-errordite.
"""
import os
from os.path import join, dirname, normpath, abspath
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(normpath(join(abspath(__file__), os.pardir)))

# this is a duplicate of django_errordite.__init__.py - which we can't
# use because of a circular dependency issue (relies on errordite, which
# may not be installed).
__title__ = 'django-errordite'
__version__ = '0.5'
__author__ = 'Hugo Rodger-Brown'
__license__ = 'Simplified BSD License'
__copyright__ = 'Copyright 2013 Hugo Rodger-Brown'
__description__ = 'Errordite exception logging for Django.'
__long_desc__ = open(join(dirname(__file__), 'README.rst')).read()
__license__ = open(join(dirname(__file__), 'LICENCE.md')).read()

setup(
    name=__title__,
    version=__version__,
    packages=['django_errordite'],
    install_requires=['errordite>=0.3'],
    include_package_data=True,
    license=__license__,
    description=__description__,
    long_description=__long_desc__,
    url='https://github.com/hugorodgerbrown/python-errordite',
    author=__author__,
    author_email='hugo@rodger-brown.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
