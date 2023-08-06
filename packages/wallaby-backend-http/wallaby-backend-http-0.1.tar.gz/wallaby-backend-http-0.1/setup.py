# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from setuptools import setup, find_packages
import os

setup(name='wallaby-backend-http',
      version='0.1',
      url='https://github.com/FreshXOpenSource/wallaby-backend-http',
      author='FreshX GbR',
      author_email='wallaby@freshx.de',
      license='BSD',
      description='Wallaby backend for http(s).',
      long_description=open('README.md').read(),
      packages=find_packages('.'),
      package_data={'': ['LICENSE', 'AUTHORS', 'README.md']},
      install_requires=['pyOpenSSL', 'twisted']
  )
