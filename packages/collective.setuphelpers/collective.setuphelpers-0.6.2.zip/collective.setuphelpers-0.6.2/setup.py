from setuptools import setup, find_packages
import os

version = '0.6.2'

setup(name='collective.setuphelpers',
      version=version,
      description="Various simple functions to be used in Plone's setuphandlers",
      long_description=open(os.path.join("collective", "setuphelpers", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone setup setuphandlers',
      author='Fry-IT',
      author_email='matous@fry-it.com',
      url='http://www.fry-it.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require = {
          'test': [
              'plone.testing [z2,]',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
