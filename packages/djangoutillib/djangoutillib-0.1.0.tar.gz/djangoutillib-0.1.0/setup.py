from distutils.core import setup
from setuptools import find_packages

setup(
    name='djangoutillib',
    version='0.1.0',
    author='Edwin van Opstal',
    author_email='evo.se-technology.com',
    url='http://github.com/EdwinvO/djangoutillib',
    license='LICENSE.txt',
    description='Collection of generic django utilities',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.1.1",
    ],
    packages=find_packages(),
)
