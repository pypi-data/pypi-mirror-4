#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# sitevcs package.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import site


sDirThis = os.path.dirname( os.path.abspath( __file__ ) )
lDir = sDirThis.split( os.sep )
##  Check directories from current and up.
for i in range( len( lDir ) )[ :: -1 ] :
  ##! |{lng:py}"/foo".split( os.sep ) == [ '', 'foo' ]|
  if lDir[ i ] :
    ##! Not |os.path.join| since it will join 'c:' and 'foo' as 'c:foo'.
    root = os.sep.join( lDir[ : i + 1 ] )
  else :
    root = '/'
  ##! 'c:' on windows as first path component.
  if root.endswith( ':' ) :
    root += '\\'
  lContent = os.listdir( root )
  if set( [ '.svn', '.hg', '.git', '.sitevcs_root' ] ) & set( lContent ) :
    break
else :
  root = ""

if root :
  site.addsitedir( root )

