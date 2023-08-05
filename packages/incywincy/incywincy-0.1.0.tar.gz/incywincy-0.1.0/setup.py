#!/usr/bin/env python
# # coding: utf-8

from setuptools import setup
from incywincy import __version__


setup(
    name='incywincy',
    description='Web Spider Testing Framework',
    long_description='A framework to easily run tests by spidering through a site',
    version=__version__,
    author='Carles Barrobés',
    author_email='carles@barrobes.com',
    url='https://github.com/txels/incywincy',
    packages=['incywincy'],
    install_requires=['beautifulsoup4', 'requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
)
