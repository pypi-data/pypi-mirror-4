import os
from setuptools import setup

def read( fname ):
    return open( os.path.join( os.path.dirname(__file__), fname ) ).read()

setup(
    name = "binio",
    version = "1.2.2",
    author = u"Alejandro L\xf3pez Correa",
    author_email = "alc@spika.net",
    description = 'A python module to simplify reading and writing binary files (or file-like objects). This module is a convenience layer on top of standard python module "struct".',
    license = "MIT license",
    keywords = "io, binary, struct, file",
    url = "http://spika.net/py/binio/",
    packages = ['binio'],
    py_modules = [],
    long_description = read('README.txt'),
    classifiers= [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
    ],
)
