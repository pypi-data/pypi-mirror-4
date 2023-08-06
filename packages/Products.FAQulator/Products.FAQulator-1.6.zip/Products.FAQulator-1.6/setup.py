from setuptools import setup, find_packages
import os

version = '1.6'

setup(name='Products.FAQulator',
      version=version,
      description="This product implements a simple FAQ content type.",
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),

      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='https://github.com/zestsoftware/Products.FAQulator',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
