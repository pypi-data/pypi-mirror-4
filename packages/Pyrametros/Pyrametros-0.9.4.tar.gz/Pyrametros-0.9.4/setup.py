import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Pyrametros",
    version = "0.9.4",
    author = "Chris Perivolaropoulos",
    author_email = "darksaga2006@gmail.com",
    description = ("A way to use ascii tables to automatically generate code."),
    license = "GPL",
    keywords = "paramtetric source code table",
    url = "http://packages.python.org/Pyrmetros",
    packages=['pyrametros', 'pyrametros.examples', 'pyrametros.test'],
    install_requires=['nose'],
    long_description=read('README.md'),
    test_suite='pyrametros.test',
    classifiers=[
        "Programming Language :: Python :: 2.7",
	"License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
    ],
)
