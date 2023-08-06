from setuptools import setup, find_packages
import os

version = '1.0b2'

setup(name='Products.MenuNavigation',
      version=version,
      description="A simple addition to the navigation menus for extra information",
      long_description=open(os.path.join("Products", "MenuNavigation", "readme.txt")).read() + "\n" +\
                       open(os.path.join("Products", "MenuNavigation", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone navigation information',
      author='Nidelven IT LTD',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products.MenuNavigation'],
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
