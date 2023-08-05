from setuptools import setup, find_packages
import os

version = '0.9dev0'

long_description = (
        '\n'.join([
            open('README.rst').read(),
            'Contributors',
            '============',
            open('CONTRIBUTORS.txt').read(),
            open('CHANGES.txt').read()
            ])
        )

setup(name='plomino.tablib',
      version=version,
      description="Make Tablib by Kenneth Reitz available to PlominoUtils.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Jean Jordaan',
      author_email='jean.jordaan@gmail.com',
      url='http://github.com/jean/plomino.tablib',
      license='gpl',
      packages=find_packages('.'),
      namespace_packages=['plomino'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.CMFPlomino',
          'tablib',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
