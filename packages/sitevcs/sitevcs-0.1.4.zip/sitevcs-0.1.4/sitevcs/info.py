#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pyrewriting library information.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import pkg_resources

NAME_SHORT = "sitevcs"
VER_MAJOR = 0
VER_MINOR = 1
try :
  VER_TXT = pkg_resources.require( NAME_SHORT )[ 0 ].version
##  Installing via 'setup.py develop'?
except pkg_resources.DistributionNotFound :
  VER_BUILD = 0
  VER_TXT = ".".join( map( str, [ VER_MAJOR, VER_MINOR, VER_BUILD ] ) )
DIR_THIS = os.path.dirname( os.path.abspath( __file__ ) )
NAME_FULL = "Python Rewriter Library"
DESCR = """
{s_name_short} v. {s_ver_txt}\\n\\n
After importing, will add nearest version control system root as site-package
directory. Used in scripts that are stored in VCS and need to import
third-party python packages that are stored in same VCS.
""".replace( '\n', '' ).replace( '\\n', '\n' ).strip().format(
  s_name_short = NAME_SHORT,
  s_ver_txt = VER_TXT )

