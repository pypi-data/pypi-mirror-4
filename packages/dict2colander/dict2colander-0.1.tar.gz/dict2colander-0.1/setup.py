#!/usr/bin/env python
from distutils.core import setup

setup(
    name="dict2colander",
    version="0.1",
    description='Dictionary to Colander schema conversion library',
    author='Peter Facka',
    url='https://bitbucket.org/pfacka/dict2colander',
    author_email='pfacka@binaryparadise.com',
    keywords='schema validation dictionary Colander YAML JSON',
    license='MIT Licence (http://opensource.org/licenses/MIT)',
    packages=[
        'dict2colander',
    ],
    requires=[
        'colander(>=1.0)',
    ],
    provides=['dict2colander (0.1)'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: POSIX',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'License :: OSI Approved :: MIT License',
      ],
)
