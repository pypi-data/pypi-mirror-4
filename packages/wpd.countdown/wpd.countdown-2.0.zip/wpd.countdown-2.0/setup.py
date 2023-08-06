# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '2.0'

long_description = (
    open('README.txt').read()
    + '\n\n' +
    'History\n'
    '=======\n'
    + '\n\n' +
    open('HISTORY.txt').read()
    + '\n')

setup(name='wpd.countdown',
      version=version,
      description="Countdown portlet for the World Plone Days",
      long_description=long_description,
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone worldploneday wpd countdown portlet',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='https://github.com/collective/wpd.countdown',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wpd'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.registry',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
