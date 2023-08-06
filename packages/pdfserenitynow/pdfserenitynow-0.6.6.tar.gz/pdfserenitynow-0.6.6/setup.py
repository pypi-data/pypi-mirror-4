#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.6.6'

setup(name='pdfserenitynow',
    version=version,
    description="Create TIFs and JPGs from crappy PDFs",
    long_description=README + '\n\n' + NEWS,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.2',
                 'Topic :: Multimedia :: Graphics :: Graphics Conversion',
                 'Topic :: Printing',
                 'Topic :: Utilities'
    ],
    keywords='pdf print converter tiff jpg',
    author='Ben Rousch',
    author_email='brousch@gmail.com',
    url='https://sourceforge.net/p/pdfserenitynow/',
    license='MIT',
    packages=["pdfserenitynow"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points={
        'console_scripts':
            ['serenifypdf=pdfserenitynow.serenifypdf:main',]
    }
)
