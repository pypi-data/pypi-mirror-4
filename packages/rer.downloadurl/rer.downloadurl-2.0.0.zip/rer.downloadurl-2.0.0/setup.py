from setuptools import setup, find_packages
import os

version = '2.0.0'

setup(name='rer.downloadurl',
      version=version,
      description="Fix the download url of Plone files, adding also the file name to it",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        ],
      keywords='file download url plone plonegov',
      author='Redturtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/rer.downloadurl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rer'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone>4.0b1'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
