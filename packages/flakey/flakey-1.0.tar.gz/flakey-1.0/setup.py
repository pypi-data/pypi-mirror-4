#!/usr/bin/python
# (c) 2005-2009 Divmod, Inc.  See LICENSE file for details

from distutils.core import setup

setup(
    name="flakey",
    license="MIT",
    version="1.0",
    description="passive checker of Python programs (py3k port)",
    maintainer="Ian Cordasco",
    maintainer_email="graffatcolmingov@gmail.com",
    url="http://bitbucket.org/icordasc/flakey",
    packages=["flakey", "flakey.scripts", "flakey.test"],
    scripts=["bin/flakey"],
    long_description=open('README').read(),
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ]
)
