# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):

    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    except IOError:
        return ''

setup(
    name="xlsimport",

    version=__import__('xlsimport').__version__,
    description=read('DESCRIPTION'),

    license="BSD",
    keywords="xls xlrd import schema",

    author="Ivan Gromov",

    author_email="summer.is.gone@gmail.com",

    maintainer='Ivan Gromov',
    maintainer_email='summer.is.gone@gmail.com',

    url="http://github.com/summerisgone/xlsimport",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',


        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',

        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    packages=find_packages(exclude=['tests']),

    install_requires=['xlrd', 'dateutils'],
    include_package_data=True,
    zip_safe=False,

    long_description=read('README')
)
