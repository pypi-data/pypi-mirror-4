""" EEA EPub Installer
"""
from setuptools import setup, find_packages
import os

NAME = 'eea.epub'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="Publish Plone content in epub form",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='epub plone import',
      author='Per Thulin, David Ichim (eaudeweb), Tiberiu Ichim (eaudeweb), '
             'Antonio De Marinis (EEA), European Environment Agency (EEA)',
      author_email='webadmin@eea.europa.eu',
      url='https://svn.eionet.europa.eu/projects/Zope',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'tests']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'BeautifulSoup',
          'lxml',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
