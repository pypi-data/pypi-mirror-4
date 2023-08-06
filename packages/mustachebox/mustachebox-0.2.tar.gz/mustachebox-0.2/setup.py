# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

VERSION = "0.2"
REQUIRES = ["django(>=1.3)","docutils"]
here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="mustachebox",
    version=VERSION,
    description="django framework to create charts of data",
    long_description="""MustacheBox is a set of utilities to help you presenting graph of
various data in a Django project. Data can come from whatever source you want :

* Distant API
* Couchdb databases
* Your Django models
* ...

And could be rendered using the js library of your choice : google
charts, d3js, raphael etc... """,
    packages = find_packages(),
    package_data={ 'mustachebox':
                    ['templates/*.html',
                     'templatetags/*',
                     'static/css/*',
                     'static/js/*',
                     'templates/mustachebox/*.html',
                     'templates/mustachebox/tags/*.html',
                     ] },
    author="Yohann Gabory",
    author_email="yohann@gabory.fr",
    url="https://bitbucket.org/boblefrag/mustachebox",
    download_url="https://bitbucket.org/boblefrag/mustachebox/get/mustachebox-0.2.tar.gz",
    requires=REQUIRES,
    classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
    ],
    include_package_data=True,
    )
