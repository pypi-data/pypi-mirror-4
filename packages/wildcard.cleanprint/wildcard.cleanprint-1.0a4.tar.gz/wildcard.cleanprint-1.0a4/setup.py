from setuptools import setup, find_packages
import os

version = '1.0a4'

setup(name='wildcard.cleanprint',
      version=version,
      description="Clean Print integration for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone cleanprint',
      author='Joel Kleier',
      author_email='joel.kleier@gmail.com',
      url='http://github.com/collective/wildcard.cleanprint',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wildcard'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
      ],
      extras_require={
            'test': ['plone.app.testing', ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
