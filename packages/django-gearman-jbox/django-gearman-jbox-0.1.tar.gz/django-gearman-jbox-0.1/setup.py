# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = '0.1'

setup(
  name                 = 'django-gearman-jbox',
  version              = VERSION,
  description          = 'A convenience wrapper for Gearman clients and workers in Django/Python',
  long_description     = open('README.md').read(),
  author               = 'Nicolas Rodriguez',
  author_email         = 'nrodriguez@jbox-web.com',
  url                  = 'http://jbox-web.github.com/django-gearman-jbox/',
  download_url         = 'http://jbox-web.github.com/django-gearman-jbox/',
  keywords             = 'django, gearman, jobs, tasks, asynchronous',
  classifiers          = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],
  license              = 'MPL',
  platforms            = 'Linux',
  packages             = find_packages(),
  include_package_data = True,
  zip_safe             = False,
  install_requires     = ['gearman>=2.0.0', 'prettytable==0.5'],
)
