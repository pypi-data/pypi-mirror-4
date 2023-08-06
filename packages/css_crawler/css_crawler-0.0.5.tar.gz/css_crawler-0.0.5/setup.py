# -*- coding: utf-8 -*-
VERSION = '0.0.5'

from setuptools import setup, find_packages
import os
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(
    name='css_crawler',
    version=VERSION,
    author='Herve Coatanhay',
    author_email='herve.coatanhay@gmail.com',
    description=('''CSSCrawler is a Nagare application that parses CSS'''
                 '''styles from website URL and generate a color palette.'''),
    long_description=longdesc,
    license='BSD',
    keywords='Nagare CSS',
    url='https://bitbucket.org/Alzakath/csscrawler',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.cfg']},
    zip_safe=False,
    install_requires=('nagare', 'cssutils', 'htmlcolor', 'simplejson', 'Babel',
                      'Elixir', 'SQLAlchemy', 'pysqlite'),
    entry_points="""
      [nagare.applications]
      css_crawler = css_crawler.app:app
      """,
    message_extractors={'css_crawler': [('**.py', 'python', None)]},
    classifiers = (
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: Stackless',
    )
)
