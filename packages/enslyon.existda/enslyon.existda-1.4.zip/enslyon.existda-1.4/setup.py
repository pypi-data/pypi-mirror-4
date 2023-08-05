from setuptools import setup, find_packages
import os

version = '1.4'

setup(name='enslyon.existda',
      version=version,
      description="Connector to eXist XML Database",
      long_description=open("README.txt").read() + "\n",
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='UNIS (ENS Lyon)',
      author_email='unis@ens-lyon.fr',
      url='https://bitbucket.org/pratic/enslyon.existda',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['enslyon'],
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
