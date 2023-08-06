import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='deconf',
    version="0.1",
    py_modules=['deconf'],
    provides=['deconf'],
    author="Dustin Lacewell",
    author_email="dlacewell@gmail.com",
    url="https://github.com/dustinlacewell/deconf",
    description="An object system for building declarative configurations in Python.",
    long_description=read('README.md'),
)
