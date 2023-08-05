from setuptools import setup, find_packages
import os

version = '2.0b4'

setup(name='Products.ContentTypeValidator',
      version=version,
      description="Provides a archetypes field validator for content types of files",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Raptus AG',
      author_email='dev@raptus.com',
      url='https://github.com/Raptus/Products.ContentTypeValidator',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require=dict(test=['plone.app.testing', ]),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
