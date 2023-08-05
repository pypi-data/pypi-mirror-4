#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

this_dir = os.path.dirname(__file__)
long_description = open(os.path.join(this_dir, 'README.rst')).read()

# Hack stuff that is useful for GitHub but not understood by PyPI :-(
long_description = long_description.replace('Example usage:\n\n.. code:: python', 'Example usage::')

setup(
    name='globtailer',
    version='0.1.0',
    description="""A generator that yields lines from the most recently modified file matching a glob pattern""",
    long_description=long_description,
    keywords='generator,tail',
    author='Marc Abramowitz',
    author_email='marc@marc-abramowitz.com',
    url='https://github.com/msabramo/python-globtailer',
    packages=['globtailer'],
    test_suite='globtailer.tests',
    entry_points={
        'console_scripts': [
            'globtailer = globtailer.main:console_script',
        ],
    },
    use_2to3=True,
    zip_safe=False,
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Testing',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ]
)
