from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='js.bootstrapdatepicker',
      version=version,
      description="bootstrap date picker fanstatic integration",
      long_description=open('README.rst').read(),
      classifiers=[],
      keywords='fanstatic bootstrap date widget',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['js'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'fanstatic',
            'js.jquery',
            'setuptools'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [fanstatic.libraries]
      bootstrap = js.bootstrapdatepicker:library
      """,
      )
