""" EEA Google Installer
"""
import os
from setuptools import setup, find_packages

NAME = 'eea.google'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=("This package contains useful tools for talking with "
                   "Google Analytics"),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='EEA google api plone zope python',
      author='Alin Voinea (eaudeweb), European Environment Agency',
      author_email='webadmin@eea.europa.eu',
      url="https://svn.eionet.europa.eu/projects/"
          "Zope/browser/trunk/eea.google",
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'tests']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
