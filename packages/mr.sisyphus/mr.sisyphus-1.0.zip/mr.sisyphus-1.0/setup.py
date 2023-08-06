from setuptools import setup
import os, sys

version = '1.0'

install_requires = [
  'setuptools',
  'argparse',
  'github3.py',
]

setup(name='mr.sisyphus',
      version=version,
      description="His pointless toil will never end",
      long_description=open("README.md").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Matthew Wilkes',
      author_email='matthew@matthewwilkes.co.uk',
      url='http://github.com/collective/mr.sisyphus',
      license='BSD',
      packages=['mr', 'mr.sisyphus'],
      package_dir = {'': 'src'},
      namespace_packages=['mr'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      test_suite='mr.sisyphus.tests',
      entry_points="""
      [console_scripts]
      mr.sisyphus = mr.sisyphus.king:king
      """,
      )
