# -*- coding: utf-8 -*-
from distutils.core import setup
import os

import importfs


def read(*path):
    basepath = os.path.abspath(os.path.dirname(__file__))
    return open(os.path.join(basepath, *path)).read()

setup(name='hg-importfs',
    version=importfs.__version__,
    description=importfs.__doc__,
    long_description=read('README.rst') + '\n' + read('CHANGELOG.rst'),
    author='Markus Zapke-Gründemann',
    author_email='markus@keimlink.de',
    url='https://bitbucket.org/keimlink/hg-importfs',
    license='GNU GPLv2+',
    py_modules=['importfs'],
    classifiers=['Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control'
    ]
)
