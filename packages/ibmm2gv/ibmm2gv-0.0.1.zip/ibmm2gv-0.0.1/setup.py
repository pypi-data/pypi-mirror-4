from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='ibmm2gv',
      version=version,
      description="indentation-based mind map in Python, render by graphviz.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='mind map,graphviz',
      author='LaiYonghao',
      author_email='mail@laiyonghao.com',
      url='http://code.google.com/p/ibmm',
      license='mit',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'argparse',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      ibmm2gv = ibmm2gv.main:main
      """,
      )
