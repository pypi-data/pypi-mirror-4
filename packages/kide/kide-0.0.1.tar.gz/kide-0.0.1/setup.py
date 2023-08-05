# -*- coding: utf-8 -*-
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

from kide import kide

REPOSITORY = 'https://github.com/rodrigopmatias/kide'


setup(
    name='kide',
    description='The simples IDE for KDE',
    version=kide.__version__,
    author='Rodrigo Pinheiro Matias',
    author_email='rodrigopmatias@gmail.com',
    maintainer='Rodrigo Pinheiro Matias',
    maintainer_email='rodrigopmatias@gmail.com',
    url=REPOSITORY,
    # download_url='%s/kide-%s.tar.gz' % (REPOSITORY, kide.__version__),
    package_dir={'': 'src'},
    packages=['kide'],
    scripts=['kide']
)
