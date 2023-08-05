import os

from setuptools import setup, find_packages


setup(name='gelato.constants',
      version='0.1.3',
      description='Gelato constants',
      namespace_packages=['gelato'],
      long_description='',
      author='',
      author_email='',
      license='',
      url='',
      include_package_data=True,
      packages=find_packages(exclude=['tests']),
      install_requires=['django', 'tower'])
