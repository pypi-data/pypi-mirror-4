from setuptools import setup, find_packages
import os

version = '1.0'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='inigo.ploneanalyticswrapper',
      version=version,
      description="A wrapper for plone.analytics viewlet which adds a selectable DIV around it",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone analytics wrapper python',
      author='Inigo Consulting',
      author_email='team@inigo-tech.com',
      url='https://github.com/inigoconsulting/inigo.ploneanalyticswrapper',
      license='gpl',
      packages=find_packages(),
      namespace_packages=['inigo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone

      """,
      )
