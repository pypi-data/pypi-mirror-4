#!/usr/bin/env python
from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='esmbc',
      version='0.4',
      description='EVE Online Ship Maintenance Bay Calculator',
      long_description=long_description,
      license='GPL3',
      author='Stuart Baker',
      author_email='sdb@stuartdb.com',
      url='https://github.com/stuartdb/esmbc',
      platforms='any',
      packages=['esmbc'],
      package_data={'esmbc': ['ships.json']},
      entry_points={
        'console_scripts': [
            'esmbc = esmbc.__main__:main',
            ],
        },
      install_requires=['distribute'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Games/Entertainment'
        ]
      )
