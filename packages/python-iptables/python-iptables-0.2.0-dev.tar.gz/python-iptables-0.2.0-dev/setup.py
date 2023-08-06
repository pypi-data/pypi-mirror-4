#!/usr/bin/env python

"""python-iptables setup script"""

from distutils.core import setup, Extension

# make pyflakes happy
__pkgname__ = None
__version__ = None
execfile("iptc/version.py")

# build/install python-iptables
setup(
    name=__pkgname__,
    version=__version__,
    description="Python bindings for iptables",
    author="Nilvec",
    author_email="nilvec@nilvec.com",
    maintainer="Dhananjay Sathe",
    url="http://nilvec.com/",
    packages=["iptc"],
    package_dir={"iptc": "iptc"},
    ext_modules=[Extension("libxtwrapper",
                           ["libxtwrapper/wrapper.c"])],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Firewalls",
        "Topic :: System :: Systems Administration",
        "Operating System :: POSIX :: Linux"
    ],
    license="Apache License, Version 2.0",
)
