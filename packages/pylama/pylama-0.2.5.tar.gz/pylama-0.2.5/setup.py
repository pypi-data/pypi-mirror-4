#!/usr/bin/env python
from os import path as op
from sys import version_info

from setuptools import setup, find_packages

from pylama import version, __project__, __license__


read = lambda f: open(
    op.join(op.dirname(__file__), f)).read() if op.exists(f) else ''


install_requires = []
if version_info < (2, 7):
    install_requires.append('argparse')


meta = dict(
    name=__project__,
    version=version,
    license=__license__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    platforms=('Any'),

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    url=' http://github.com/klen/pylama',

    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'pylama = pylama.main:shell',
        ]
    },

    install_requires=install_requires,
    test_suite = 'tests',
)


if __name__ == "__main__":
    setup(**meta)
