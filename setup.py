#!/usr/bin/env python
from setuptools import setup

setup(
      name='CodeArgos',
      version='0.2',
      description='A python module for red teams to support the continuous recon of JavaScript files and HTML script blocks in an active web application.',
      long_description=open('README.md').read(),
      author='Dana Epp',
      author_email='dana@vulscan.com',
      url='https://github.com/danaepp/codeargos',
      license='MIT',
      packages=['codeargos'],
      install_requires=[ 'requests', 'colorama', 'jsbeautifier', 'urllib3', 'beautifulsoup4', 'pymsteams' ]
     )