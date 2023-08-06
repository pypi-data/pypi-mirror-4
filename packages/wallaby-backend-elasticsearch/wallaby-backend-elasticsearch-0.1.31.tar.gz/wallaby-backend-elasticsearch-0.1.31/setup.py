# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from setuptools import setup, find_packages

setup(name='wallaby-backend-elasticsearch',
      version='0.1.31',
      url='https://github.com/FreshXOpenSource/wallaby-backend-elasticsearch',
      author='FreshX GbR',
      author_email='wallaby@freshx.de',
      license='BSD',
      description='Asynchronous elasticsearch backend - part of Wallaby. The couchDB application framework.',
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
        'Topic :: Software Development :: Libraries'
      ],
      packages=find_packages("."),
      install_requires=['wallaby-backend-http']
  )
