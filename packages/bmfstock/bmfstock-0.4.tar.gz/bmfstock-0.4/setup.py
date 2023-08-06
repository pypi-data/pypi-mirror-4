'''
Created on Mar 1, 2012

@author: christofer
'''

from bmfstock import __version__ as version
from setuptools import setup

description = "Library to retrieve info about equity from BMF Bovespa"
classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ]

setup(
    name="bmfstock",
    description=description,
    version=version,
    author="Christofer Bertonha",
    author_email="christoferbertonha@gmail.com",
    py_modules=['bmfstock'],
    license="LGPL3",
    long_description=description,
    classifiers=classifiers,
)
