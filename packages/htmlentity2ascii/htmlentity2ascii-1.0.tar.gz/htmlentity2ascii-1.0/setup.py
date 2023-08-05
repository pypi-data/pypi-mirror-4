#!/usr/bin/env python
#This file is part of htmlentity2ascii.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import os
from setuptools import setup, find_packages
import htmlentity2ascii

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='htmlentity2ascii',
        version=htmlentity2ascii.__version__,
        author='Zikzakmedia',
        author_email='zikzak@zikzakmedia.com',
        url="http://stackoverflow.com/questions/1197981/convert-html-entities-to-ascii-in-python/1582036#1582036",
        description="Python module to convert html entities to ascii",
        long_description=read('README'),
        download_url="",
        packages=find_packages(),
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Office/Business :: Financial :: Accounting',
            'Topic :: Software Development :: Internationalization',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        license='GPL-3',
        extras_require={
        },
    )
