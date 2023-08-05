import os

from setuptools import setup, find_packages

if os.path.exists('README.rst'):
    with open('README.rst') as file:
        long_description = file.read()
else:
    long_description = ''

setup(
    name="txcoroutine",
    description="Coroutines for Twisted with tail call optimization support",
    long_description=long_description,
    version="1.0.9",
    packages=find_packages(),

    install_requires=[
        'twisted',
    ],

    author="Erik Allik",
    author_email="eallik@gmail.com",
    license="BSD",
    url="http://github.com/eallik/txcoroutine/"
)
