#-*- coding:utf-8 -*-
"""
pycutter
~~~~~~

pycutter is a simple screen shot tool in Python.
"""

from setuptools import setup, find_packages

setup(
        name = 'pycutter',
        version = '0.1.0',
        description = 'A simple screen shot tool',
        long_description = __doc__,
        author = 'DanielBlack',
        author_email = 'danielblack@danielblack.name',
        license = "MIT",
        url = 'http://github.com/DanielBlack/pycutter',
        packages = ['pycutter'],
        include_package_data = True,
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Environment :: X11 Applications :: Qt"
            "Intended Audience :: End Users/Desktop"
            "License :: OSI Approved :: MIT License"
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            ],
        zip_safe=False,
        extras_require={'PyQt': ['PyQt>=4.9.4']},
        )
