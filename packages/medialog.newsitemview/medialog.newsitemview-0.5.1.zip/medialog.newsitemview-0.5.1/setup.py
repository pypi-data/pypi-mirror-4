from setuptools import setup, find_packages
import os

version = '0.5.1' 

setup(name='medialog.newsitemview',
      version=version,
      description="Makes it possible to choose size for newsitem image.",
      long_description=open("README").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope newsitemview',
      author='Grieg Medialog [Espen Moe-Nilssen]',
      author_email='espen@medialog.no',
      url='http://products.medialog.no',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['medialog'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          'archetypes.markerfield',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
