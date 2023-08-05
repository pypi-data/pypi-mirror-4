# installation: easy_install ago

from setuptools import setup

setup( 
    name = 'ago',
    version = '0.0.5',
    description = 'ago: Human readable timedeltas',
    keywords = 'ago human readable time deltas timedelta datetime',
    long_description = open('README.rst').read(),

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://bitbucket.org/russellballestrini/ago/src',

    platforms = ['All'],
    license = 'Public Domain',

    py_modules = ['ago'],
    include_package_data = True,
)

# setup keyword args: http://peak.telecommunity.com/DevCenter/setuptools

# built and uploaded to pypi with this:
# python setup.py sdist bdist_egg register upload

