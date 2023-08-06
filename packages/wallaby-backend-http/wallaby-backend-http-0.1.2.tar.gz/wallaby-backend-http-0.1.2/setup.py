# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from setuptools import setup, find_packages
import os

setup(name='wallaby-backend-http',
      version='0.1.2',
      url='https://github.com/FreshXOpenSource/wallaby-backend-http',
      author='FreshX GbR',
      author_email='wallaby@freshx.de',
      license='BSD',
      description='Wallaby backend for http(s).',
      long_description=open('README.md').read(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
      ],
      package_data={'': ['LICENSE', 'AUTHORS', 'README.md']},
      packages=find_packages('.'),
      install_requires=['pyOpenSSL', 'twisted']
  )
