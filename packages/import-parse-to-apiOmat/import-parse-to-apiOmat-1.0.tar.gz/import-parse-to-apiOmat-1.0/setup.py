'''
Created on 29.04.2013

@author: phimi
'''
from setuptools import setup, find_packages
setup(
    name = "import-parse-to-apiOmat",
    description = "Import your data from Parse to apiOmat",
    url = "https://github.com/apiOmat/apiOmat-import-parse",
    version = "1.0",
    scripts=['ImportParseData/import-parse-to-apiOmat'],
    packages = find_packages(),
)