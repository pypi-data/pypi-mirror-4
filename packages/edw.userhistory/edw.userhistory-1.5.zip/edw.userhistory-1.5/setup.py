""" Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

NAME = 'edw.userhistory'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="User login history",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='David Batranu',
      author_email='david.batranu@eaudeweb.ro',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['edw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require = {
            'test': [
                'plone.app.testing',
                    ],
                        },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
