import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Franges",
    version = "0.1.0",
    author = "Nisan Haramati",
    author_email = "hanisan@gmail.com",
    description = ("Franges adds support for floating point and fixed precision (Decimal) range generator functions."),
    license = "LGPLv3+",
    maintainer = "Nisan Haramati",   
    keywords = "example documentation tutorial",
    url = "http://code.google.com/p/franges/",
    packages=['franges',],
    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    ],
)