from setuptools import setup, find_packages
import os

version = '1.4.1'

setup(name='Products.cooptation',
      version=version,
      description="Product to coopt new members for Plone. By Ecreall.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Vincent Fretin and Michael Launay',
      author_email='development@ecreall.com',
      url='https://svn.ecreall.com/public/Products.cooptation',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.grok',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
