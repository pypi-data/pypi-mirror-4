from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='Products.ScreenReaderNavigation',
      version=version,
      description="Adds header-2 HTML to navigation portlet for accessibility",
      long_description=open(os.path.join("Products", "ScreenReaderNavigation", "readme.txt")).read() +'\n\n'+\
        open(os.path.join("Products", "ScreenReaderNavigation", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        ],
      keywords='python plone accessibility navigation',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
