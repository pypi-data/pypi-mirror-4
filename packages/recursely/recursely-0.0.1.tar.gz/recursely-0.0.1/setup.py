"""
recursely
=========

Recursive importer for Python submodules

Usage
-----

First, install it early during program's initialization,
such as the top of `\_\_init\_\_.py` in its main package::

    import recursely
    recursely.install()

Then you can add::

    __recursive__ = True

anywhere in the `\_\_.init\_\_.py` file of a package
that you want to import recurs(iv)ely.

That's all to it, really.
"""
from setuptools import setup, find_packages

import recursely


setup(
    name="recursely",
    version=recursely.__version__,
    description="Recursive importer for Python submodules",
    long_description=__doc__,
    author=recursely.__author__,
    author_email="karol.kuczmarski@gmail.com",
    url="http://github.com/Xion/recursely",
    license="Simplified BSD",

    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],

    platforms='any',
    packages=find_packages(exclude=['tests']),
    tests_require=['nose'],
)
