from setuptools import setup

setup(
    name='dwolla-clt',
    license='MIT',
    version='1.2.2',
    install_requires=[
        'dwolla>=1.4.8',
        'argparse>=1.2.1'
    ],
    scripts=['bin/dwolla-clt'],
    
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