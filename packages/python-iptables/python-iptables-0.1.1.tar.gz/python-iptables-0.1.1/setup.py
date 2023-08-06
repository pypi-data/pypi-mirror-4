#!/usr/bin/env python

"""python-iptables setup script"""

import os
from distutils.core import setup, Extension

LONGSDESC= """
Python Bindings for IPtables:

Iptables is the tool that is used to manage netfilter, the standard packet filtering and manipulation framework under Linux. As the iptables manpage puts it:
Iptables is used to set up, maintain, and inspect the tables of IPv4 packet filter rules in the Linux kernel. Several different tables may be defined.
Each table contains a number of built-in chains and may also contain user- defined chains.
Each chain is a list of rules which can match a set of packets. Each rule specifies what to do with a packet that matches. This is called a target, which may be a jump to a user-defined chain in the same table.
Python-iptables provides python bindings to iptables under Linux. Interoperability with iptables is achieved via using the iptables C libraries (libiptc, libxtables, and the iptables extensions), not calling the iptables binary and parsing its output.

See http://ldx.github.com/python-iptables/ for documentation.

Usage :
import iptc

"""
execfile("iptc/version.py")

# build/install python-iptables
setup(
        name                = 'python-iptables',
        version             = __version__,
        long_description    = LONGSDESC,
        description         = "Python bindings for iptables",
        author              = "Nilvec",
        author_email        = "nilvec@nilvec.com",
        url                 = "http://nilvec.com/",
        maintainer          = 'Dhananjay Sathe',
        maintainer_email    = 'dhananjaysathe@gmail.com',
        packages            = ["iptc"],
        package_dir         = {"iptc" : "iptc"},
        ext_modules         = [Extension("libxtwrapper",
            ["libxtwrapper/wrapper.c"])],
        classifiers         = [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Topic :: System :: Networking",
            "Topic :: System :: Networking :: Firewalls",
            "Natural Language :: English",
            ],
        license    = "Apache License, Version 2.0",
        )
