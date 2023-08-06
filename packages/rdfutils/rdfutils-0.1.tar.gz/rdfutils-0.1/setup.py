import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='rdfutils',
    version='0.1',
    description='Thin wrapper functions to work with an RDF store based on the Redland C library & Python bindings (python-librdf)',
    author='Michael Murtaugh',
    author_email='mm@automatist.net',
    url='http://git.constantvzw.org/aa.rdfutils.git',
    py_modules=['rdfutils'],
    license = "GPL3",
    keywords = "rdf",
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Text Processing :: Indexing"
    ],
)
