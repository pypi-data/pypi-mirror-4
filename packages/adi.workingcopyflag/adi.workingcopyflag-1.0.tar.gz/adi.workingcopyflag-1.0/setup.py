from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='adi.workingcopyflag',
      version=version,
      description="Makes it possible to flag items as 'special'.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope flag important iterate workingcopy index catalog collections topics',
      author='Ida Ebkes',
      author_email='contact@ida-ebkes.eu',
      url='http://plone.org/products/adi.workingcopyflag',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['adi'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          'archetypes.markerfield',
          'plone.app.iterate',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
