# -*- coding: utf-8 -*-
'''
    Copyright (C) 2013  Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from distutils.core import setup

import sys
import os

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'src'
    )
)

from kidelib import kide


def check_library(library):
    try:
        exec('import %s' % library)
    except ImportError:
        raise Exception('Cant install without %s you need install this first.' % library)

check_library('PyQt4')
check_library('PyQt4.Qsci')

setup(
    name='kide',
    description='The simples IDE for KDE',
    version=kide.__version__,
    author='Rodrigo Pinheiro Matias',
    author_email='rodrigopmatias@gmail.com',
    maintainer='Rodrigo Pinheiro Matias',
    maintainer_email='rodrigopmatias@gmail.com',
    url=kide.REPOSITORY,
    package_dir={'': 'src'},
    packages=['kidelib', 'kidelib.gui', 'kidelib.gui.ui'],
    install_requires=[],
    scripts=['kide']
)
