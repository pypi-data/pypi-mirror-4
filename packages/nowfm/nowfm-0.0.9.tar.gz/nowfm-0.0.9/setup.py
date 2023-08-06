from setuptools import setup

version = '0.0.9'
name = 'nowfm'
short_description = '`nowfm` is a package for get track information from Last.fm.'
long_description = """\
`nowfm` is a package for get track information from Last.fm.

Requirements
------------
* Python 2.7 or later (not support 3.x)

Features
--------
* Additional information about when user played track

Setup
-----
::

   $ pip install nowfm

History
-------
0.0.9 (2013-03-24)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "License :: OSI Approved :: Python Software Foundation License",
    "Programming Language :: Python",
    "Topic :: Software Development",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    keywords=['Last.fm library',],
    author='cloverrose',
    author_email='example@example.com',
    url='https://github.com/cloverrose/nowfm',
    license='PSL',
)
