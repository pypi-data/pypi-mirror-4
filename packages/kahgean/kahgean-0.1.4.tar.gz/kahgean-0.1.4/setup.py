# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

from distutils.core import setup

__version__ = "0.1.4"

with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name = "kahgean",
    version = __version__,
    packages = ["kahgean"],
    author = "Xue Can",
    author_email = "xuecan@gmail.com",
    url = "https://bitbucket.org/xuecan/kahgean",
    keywords = ["command-line", "configuration", "logging", "daemonize"],
    description = "a set of handy utils for daily development",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description = long_description
)
