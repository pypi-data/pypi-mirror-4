#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

_long_description_ = """
Description:

dyndnsc is both a script to be used directly as well as a re-usable and
hopefully extensible collection of classes for doing updates to dynamic
dns services.

Design:

- updating a dyndns entry is done by a "DynDNS Update Protocol handler"
- detecting IPs, both in DNS or elsewhere is done using IPDetector's
  which all have a detect() method and bookkeeping about changes
- the DynDnsClient uses the Protocol Handler to do the updates and
  the IPDetectors to decide when an update needs to occur
- a dummy endless loop ( used for time.sleep() ) repeatedly asks the
  DynDnsClient to make sure everything is fine

Features:

- relatively easy to embed in your own application (see main() for an example)
- Growl desktop notification support (optional)

Example use::

    python dyndnsc.py  --hostname test.dyndns.com --userid bob \
      --method=Iface,netmask:2001:0000::/32,iface:tun0,family:INET6

Other:

probably works with python 2.3, 2.4 tested with python 2.5, 2.6 and 2.7
"""

classifiers = filter(None, map(str.strip,
"""
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: DFSG approved
License :: OSI Approved
License :: OSI Approved :: MIT License
Topic :: Internet :: Name Service (DNS)
Topic :: Software Development :: Libraries :: Python Modules
Environment :: Console
Natural Language :: English
Operating System :: MacOS :: MacOS X
Operating System :: POSIX :: Linux
Operating System :: POSIX :: BSD :: FreeBSD
Programming Language :: Python
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
""".splitlines()))

setup(name='dyndnsc',
      py_modules=['dyndnsc'],
      version='0.2.1',
      author="Paul Kremer",
      author_email="@".join(("paul", "spurious.biz")),  # avoid spam
      license="MIT License",
      description="dynamic dns update client module that tries to be extensible, re-usable and efficient on network resources",
      long_description=_long_description_,
      url="http://pol.spurious.biz/dyndnsc/",
      install_requires=[
                          "IPy>=0.56",
                          "netifaces>=0.4",
                          ],
      entry_points=("""
                      [console_scripts]
                      dyndnsc=dyndnsc:main
                      """),
      classifiers=classifiers,
      )
