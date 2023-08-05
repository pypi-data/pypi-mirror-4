import os
import sys

from setuptools import setup, find_packages

requires = [
    'wtforms',
    ]

setup(name='wtdojo',
      version='0.1.2',
      description='Dojo javascript toolkit support for WTForms',
      long_description="""Adds support to display Dojo form fields via WTForms""",
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        ],
      author='Kashif Iftikhar',
      author_email='kashif@compulife.com.pk',
      url='http://pypi.python.org/pypi/wtdojo',
      keywords='wtforms dojo',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires
      )

