# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='sphinxcontrib-recentpages',
      version='0.6.1',
      author='Sho Shimauchi',
      author_email='sho.shimauchi@gmail.com',
      url='https://bitbucket.org/shiumachi/sphinxcontrib-recentpages',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
        ],
      test_suite='nose.collector',
      tests_require='Nose',
      packages=find_packages(),
      namespace_packages=['sphinxcontrib'],
      )
