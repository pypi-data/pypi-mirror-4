# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from setuptools import setup, find_packages

setup(name='wallaby-plugin-couchdb',
      version='0.1.12',
      url='https://github.com/FreshXOpenSource/wallaby-plugin-couchdb',
      author='FreshX GbR',
      author_email='wallaby@freshx.de',
      license='BSD',
      description='This package integrates the couchdb backend into wallaby.',
      long_description=open('README.md').read(),
      package_data={'': ['LICENSE', 'AUTHORS', 'README.md']},
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
        'Topic :: Software Development :: Libraries :: Application Frameworks'
      ],
      packages=find_packages('.'),
      install_requires=['wallaby-backend-couchdb']
  )
