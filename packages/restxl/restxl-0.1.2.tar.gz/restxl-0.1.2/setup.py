'''
Created on Jun 28, 2010

@author: brianjinwright
'''
from setuptools import setup, find_packages
 
version = '0.1.2'
 
LONG_DESCRIPTION = """
=====================================
RestXL (python REST framework)
=====================================

This project exists to make it easier to create REST clients that are also
very easy to understand. 

The cores of this project are requests, url variables, headers, and RestXLers.

================
New in 0.1.2
================

- Computations and Constants
"""
 
setup(
    name='restxl',
    version=version,
    description="This project exists to make it easier to create client libraries for REST APIs that are also"
    "very easy to understand.",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
    ],
    keywords='rest,django,declarative,api,web',
    author='Brian Jinwright',
    author_email='team@ipoots.com',
    maintainer='Brian Jinwright',
    packages=find_packages(),
    url='https://bitbucket.org/brianjinwright/restxl',
    license='MIT',
    install_requires=['BeautifulSoup==3.2.0','simplexmlapi==0.1.2',
                      'requests==0.10.1'],
    include_package_data=True,
    zip_safe=False,
)