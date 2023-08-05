#!/usr/bin/env python

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


import sys
import os
from setuptools import setup, find_packages, Extension

description_txt = file('README.txt').read()
description_txt += '\n\nChanges\n-------\n\n'
description_txt += file('CHANGES.txt').read()

version = '3.6.1.1'

setup(name="zopyx.txng3.core",
      version = version,
      packages=('zopyx', 'zopyx.txng3', 'zopyx.txng3.core', 'textindexng'),
      maintainer= "Andreas Jung, ZOPYX Ltd.",
      maintainer_email = "info@zopyx.com",
      author = "Andreas Jung, ZOPYX Ltd.",
      author_email = "info@zopyx.com",
      description = 'TextIndexNG3 core implementation',
      long_description = description_txt,
      url = "http://sf.net/projects/textindexng/",
      include_package_data=True,
      install_requires=('setuptools',
                        'ZODB3',
                        'zope.component',
                        'zope.componentvocabulary',
                        'zope.interface',
                        'zopyx.txng3.ext',
                        ),
      test_suite='nose.collector',
      namespace_packages=('zopyx', 'zopyx.txng3'),
      tests_require=('nose', 'zope.testing'),
      extras_require=dict(
        test=('nose', 'zope.testing'),
      ),
    )
