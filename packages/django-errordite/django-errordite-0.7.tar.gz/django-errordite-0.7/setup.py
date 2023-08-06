"""
Setup file for django-errordite.
"""
import os
from os.path import join, dirname, normpath, abspath
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(normpath(join(abspath(__file__), os.pardir)))

# we can't import errordite as it hasn't been installed yet, so instead
# read information in as text. This will read in the __init__ file, and
# create a dict containing any lines beginning with '__' as keys, with
# whatever is after the '=' as the value,
# __desc__ = 'hello'
# would give {'desc': 'hello'}
meta = {}
for l in [line for line in tuple(open('django_errordite/__init__.py', 'r')) if line[:2] == '__']:
    t = l.split('=')
    meta[t[0].strip().strip('__')] = t[1].strip().strip('\'')

setup(
    name=meta['title'],
    version=meta['version'],
    packages=['django_errordite'],
    install_requires=['errordite>=0.4'],
    include_package_data=True,
    license=open(join(dirname(__file__), 'LICENCE.md')).read(),
    description=meta['description'],
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    url='https://github.com/hugorodgerbrown/django-errordite',
    author=meta['author'],
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
