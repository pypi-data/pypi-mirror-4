#-*- coding:utf-8 -*-
"""
pyminidict
~~~~~~

pyminidict, is a mini CLI English/Chinese dictionary drived by python, which relies on YouDao(有道) online dictionary.
"""

from setuptools import setup, find_packages

setup(
        name = 'pyminidict',
        version = '0.1.0',
        description = 'A mini CLI English/Chinese dictionary',
        long_description = __doc__,
        author = 'DanielBlack',
        author_email = 'danielblack@danielblack.name',
        license = "MIT",
        url = 'http://github.com/DanielBlack/pyminidict',
        packages = ['pyminidict'],
        include_package_data = True,
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Environment :: X11 Applications",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            ],
        zip_safe=False,
        extras_require={'pyquery': 'pyquery>0.1'}, 
        )
