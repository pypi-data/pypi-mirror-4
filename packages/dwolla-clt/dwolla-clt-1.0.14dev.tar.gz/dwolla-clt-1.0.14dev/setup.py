#!/usr/bin/env python

from setuptools import setup

setup(
    name='dwolla-clt',
    license='MIT',
    py_modules=['dwolla-clt'],
    version='1.0.14dev',
    install_requires=open('requires.txt').read(),
    
    description='Dwolla Command Line Tools',
    long_description=open('README.rst').read(),
    
    author='Michael Schonfeld',
    author_email='michael@dwolla.com',
    url='https://github.com/dwolla/dwolla-clt',
    
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Topic :: Office/Business :: Financial :: Point-Of-Sale',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)