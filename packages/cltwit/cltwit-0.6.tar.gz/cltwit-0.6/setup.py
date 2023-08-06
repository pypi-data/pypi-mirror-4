# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages
import sys, os

version = '0.6'

setup(name='cltwit',
        version=version,
        description="'Command line Twitter utility'",
        long_description=open('README.rst').read(),
        # quelques metadata, liste complete http://is.gd/AajTjj
        classifiers=[
          "Programming Language :: Python",
          "Natural Language :: French",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Topic :: Terminals",
          'Topic :: Utilities',
          ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        keywords="'twitter command-line follow unfollo export tweet'",
        author='Jérôme Launay'.decode('utf-8'),
        author_email='jerome@projet-libre.org',
        url='http://forge.projet-libre.org/projects/cltwit/wiki',
        license='WTFPL',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        namespace_packages=(['cltwit']),
        # Active la prise en compte du fichier MANIFEST.in
        include_package_data=True,
        zip_safe=False,
        # dépendances
        install_requires=["tweepy", "reportlab"],
        entry_points={
            'console_scripts': [
                'cltwit = cltwit.main:main',
            ]
        },
      )
