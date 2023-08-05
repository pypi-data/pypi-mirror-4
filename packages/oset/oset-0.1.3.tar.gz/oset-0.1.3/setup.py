#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Main setup.py file"""


from setuptools import setup, find_packages
import os

version = '0.1.3'
shortdesc = 'Ordered Set.'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(name='oset',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: Python Software Foundation License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development',
      ],
      keywords='oset ordered set collection',
      url='https://gitorious.com/sleipnir/python-oset',
      license='Python Software Foundation License',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      maintainer="Carlos Martin",
      maintainer_email="inean.es@gmail.com",
      namespace_packages=[],
      include_package_data=True,
      zip_safe=True,
      install_requires=['setuptools'],
      test_suite="oset.tests.test_suite",
)
