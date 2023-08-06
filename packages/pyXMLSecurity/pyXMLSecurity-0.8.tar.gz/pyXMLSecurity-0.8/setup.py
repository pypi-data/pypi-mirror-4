#!/usr/bin/env python
from setuptools import setup, find_packages
import sys, os
from distutils import versionpredicate

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.8'

install_requires = [
    'lxml'
]

setup(name='pyXMLSecurity',
    version=version,
    description="pure Python XML Security",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='xml xml-dsig security digital signature rsa',
    author='Leif Johansson',
    author_email='leifj@sunet.se',
    url='http://blogs.mnt.se',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    package_data = {
    },
    zip_safe=False,
    install_requires=install_requires,
    requires=install_requires
)
