#!/usr/bin/env python

from setuptools import setup, find_packages
import io
import os

here = os.path.abspath(os.path.dirname(__file__))

NAME = 'bzzz'

# Import version from file
version_file = open(os.path.join(here, 'VERSION'))
VERSION = version_file.read().strip()

DESCRIPTION = 'Bzzz is a quadcopter'


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=['Naga Venkata Sai Chandra Mouli',
              'Jamie Rainey', 'Pantelis Sopasakis'],
      author_email='p.sopasakis@gmail.com',
      license='MIT License',
      packages=find_packages(
          exclude=["tests/"]),
      include_package_data=True,
      install_requires=[
          'smbus', 'pigpio', 'bitarray', 'pyserial', 'VL53L0X', 'pandas', 'numpy', 'matplotlib', 'wheel', 'control'
      ],
      dependency_links=[
          "git+https://github.com/pimoroni/VL53L0X-python.git",
      ],
      classifiers=[
          'Topic :: Software Development :: Embedded Systems'
      ],
      keywords=['embedded'],
      url=(
          'https://github.com/QUB-ASL/bzzz'
      ),
      zip_safe=False)
