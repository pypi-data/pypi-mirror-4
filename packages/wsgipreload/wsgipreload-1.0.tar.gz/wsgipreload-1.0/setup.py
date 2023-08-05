from distutils.core import setup
from setuptools import find_packages
import setuptools # for extra commands

setup(
    name = 'wsgipreload',
    packages = find_packages(),
    version = '1.0',
    description = 'Preload WSGI applications by running a few URLs through the app immediately when it starts',
    author = 'Dave Brondsema',
    author_email = 'dave@brondsema.net',
    license = 'Apache License',
    url = 'https://sourceforge.net/p/wsgipreload/',

    requires = ['webob'],
)
