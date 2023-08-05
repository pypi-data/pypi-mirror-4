from setuptools import setup, find_packages
import sys, os

version = '1.0rc3'

setup(name='lelo',
      version=version,
      description="Utilities for easy parallelisation of tasks",
      long_description="""\
""",
      classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: No Input/Output (Daemon)",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: Implementation :: PyPy",
          ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python parallel highperformance multicore core thread multithread python2',
      author='Joao S. O. Bueno',
      author_email='jsbueno@simplesconsultoria.com.br',
      url='https://bitbucket.org/jsbueno/lelo',
      license='LGPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
