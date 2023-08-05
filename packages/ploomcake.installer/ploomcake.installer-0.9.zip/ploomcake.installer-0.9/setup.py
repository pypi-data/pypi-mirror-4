from setuptools import setup, find_packages
import os

version = '0.9'

setup(name='ploomcake.installer',
      version=version,
      description="Ploomcake instance installer",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Maurizio Lupo',
      author_email='maurizio.lupo@redomino.com',
      url='https://github.com/ploomcake/ploomcake.installer',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ploomcake'],
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
