#!/usr/bin/env python

from setuptools import setup

def linelist(text):
    """
    Returns each non-blank line in text enclosed in a list.
    """
    return [ l.strip() for l in text.strip().splitlines() if l.strip() ]

setup(
    name='enpassant',
    version='0.2',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='En passant assignment for clearer if and while control structures',
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/jeunice/enpassant',
    packages=['enpassant'],
    install_requires=[],
    tests_require = ['tox', 'pytest'],
    zip_safe = False,  # actually it is, but this apparently avoids setuptools hacks
    keywords='en passant',
    classifiers=linelist("""
        Development Status :: 3 - Alpha
        Operating System :: OS Independent
        License :: OSI Approved :: BSD License
        Intended Audience :: Developers
        Programming Language :: Python
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: PyPy
        Topic :: Software Development :: Libraries :: Python Modules
    """)
)
