"""
setup.py for jira-cli
"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org"

import os
import sys
from setuptools import setup, find_packages, Command

version="0.2.8"

setup(name='jira-cli',
     author="Ali-Akber Saifee",
     author_email="ali@indydevs.org",
     url="http://hg.indydevs.org/jira-cli",
     version = version,
     description = "command line utility for interacting with jira",
     long_description = open("README.txt").read(),
     packages = find_packages(exclude=['ez_setup']),
     include_package_data = True,
     zip_safe = False,
     install_requires =[
         'setuptools',
         'termcolor'
         ],
     entry_points = {
         'console_scripts' : [
             'jira-cli = jiracli.cli:main',
             ]
        },
     )

