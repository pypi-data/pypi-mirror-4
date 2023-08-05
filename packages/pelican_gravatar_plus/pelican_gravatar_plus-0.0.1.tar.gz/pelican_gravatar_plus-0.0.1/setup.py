# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

description = 'Pelican Plugin to pull Gravtars'
long_description = open('README.md').read() if os.path.exists('README.md') else ""

version = "0.0.1"

setup(name='pelican_gravatar_plus',
      version=version,
      install_requires=[
          'requests==0.14.0',
          'pelican==3.1',
      ],
      packages=find_packages(),
      author='Michele Memoli',
      url='https://bitbucket.org/redmonkey/pelican-plugin-gravatar-plus',
      author_email='michele@100shapes.com',
      description=description,
      long_description=long_description,
      platforms=['any'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)