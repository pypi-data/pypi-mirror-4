#!/usr/bin/env python
import os
import sys
from setuptools import setup

import remembeep as package


doc = package.__doc__.strip()
open('README.md', 'w').write(doc)
if sys.argv[-1] == 'publish':
    if not package.run_tests().failed:
        os.system('python setup.py sdist upload')
        sys.exit(0)

setup(
    name         = package.__name__,
    url          = 'https://github.com/imbolc/%s' % package.__name__,
    version      = package.__version__,
    description  = doc.split('===\n')[1].strip().split('\n\n')[0],
    long_description = doc,

    #py_modules   = [package.__name__],
    packages   = [package.__name__],

    #package_data = {package.__name__: ['default.mp3']},
    #include_package_data = True,

    install_requires = ['argparse', 'simple_daemon'],

    entry_points = {
        'console_scripts': [
            'remembeep = remembeep:main',
        ]
    },

    author       = 'Imbolc',
    author_email = 'imbolc@imbolc.name',
    license      = 'ISC',

    classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ],
)
