'''
Author  : Sourabh Bajaj
Date    : 26th April, 2013
Email   : sourabhbajaj@gatech.edu
Summary : Setup file for DemoPackage
License : BSD License
'''

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name='DemoPackage',
    version='0.0.1',
    author='Sourabh Bajaj',
    packages=find_packages(),
    namespace_packages=['DemoPackage'],
    include_package_data=True,
    url='http://sb2nov.github.io/DemoPackage',
    long_description=open('README.md').read(),
    author_email='sourabhbajaj90@gmail.com',
    license=open('LICENSE.txt').read(),
    description='QuantSoftware Toolkit',
    install_requires=[
        "setuptools",
    ],
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
