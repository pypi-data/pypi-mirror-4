# -*- coding: utf-8 -*-
import sys
from os import path
from distutils.core import setup

if sys.version_info < (2, 6):
    sys.exit('fx requires Python 2.6 or higher')

ROOT_DIR = path.abspath(path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from fx import VERSION
from fx import __doc__ as DESCRIPTION
LONG_DESCRIPTION = open(path.join(ROOT_DIR, 'README.rst')).read()

setup(
    name='fx',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author='Philip Xu',
    author_email='pyx@xrefactor.com',
    url='https://bitbucket.org/pyx/fx',
    download_url=(
        'https://bitbucket.org/pyx/fx/get/%s.tar.bz2' % VERSION),
    packages=['fx'],
    license='BSD-New',
)
