from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='mtj.f3u1',
      version=version,
      description="Factory For Formatting Units",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("mtj", "f3u1", "README.rst")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Tommy Yu',
      author_email='y@metatoaster.com',
      url='https://github.com/metatoaster/mtj.f3u1',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mtj'],
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
