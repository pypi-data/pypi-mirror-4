from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='TinkerPy',
      version=version,
      description="Tools tinkering with basic Python stuff.",
      long_description='''\
      This Python project contains the package ``tinkerpy`` which provides:

      *   special dictionary implementations
      *   a function to flatten data structures composed of iterables
      *   some useful decorators
      *   a function to create an UTF-16 string from an Unicode codepoint
      ''',
      classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Python Modules'
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='tool decorator dict mapping Unicode',
      author='Michael Pohl',
      author_email='pohl-michael@gmx.biz',
      url='https://github.com/IvIePhisto/TinkerPy',
      license='MIT License',
      packages=find_packages(exclude=['tests']),
      test_suite='tests',
      include_package_data=True,
      zip_safe=True,
)
