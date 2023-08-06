#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Sat Jul  9 20:21:55 CEST 2012

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.utils',
    version='1.0.2',
    description='Utilitary package for antispoofing countermeasures',
    url='http://pypi.python.org/pypi/antispoofing.utils',
    license='GPLv3',
    author='Tiago de Freitas Pereira',
    author_email='tiagofrepereira@gmail.com',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data = True,
    zip_safe = False,

    install_requires=[
      "setuptools",
      "bob >= 1.1.0",
    ],

    namespace_packages = [
      'antispoofing',
      ],

    entry_points={
      'console_scripts': [
        'merge_scores.py = antispoofing.utils.script.merge_scores:main',
        'test_db.py = antispoofing.utils.script.test_db:main',
        ],
      },

    classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
	)
