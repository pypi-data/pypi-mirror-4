#!/usr/bin/env python
"""
Installation script:

To release a new version to PyPi:
- Ensure the version is correctly set in oscar.__init__.py
- Run: python setup.py sdist upload
"""

from setuptools import setup, find_packages

setup(name='django-mailup',
      version="0.1.1",
      url='https://bitbucket.org/marcominutoli/django-mailup.git',
      author="Marco Minutoli",
      author_email="info@marcominutoli.it",
      description="A plugin to integrate Django and Mailup",
      long_description=open('README.rst').read(),
      keywords="Newsletter, Django, Mailup",
      license='BSD',
      packages=find_packages(),
      install_requires=[
          'suds==0.4',
      ],
      # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: Unix',
                   'Programming Language :: Python']
      )
