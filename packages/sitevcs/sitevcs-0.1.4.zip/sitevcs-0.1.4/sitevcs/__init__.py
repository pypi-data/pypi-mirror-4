#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# sitevcs package.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import site
import inspect


##  Path (may be relative to current dir) of file that used 'import' on
##  this package.
sFileImporter = inspect.currentframe().f_back.f_code.co_filename
sDirImporter = os.path.dirname( os.path.abspath( sFileImporter ) )

##  Check directories from importer's and up.
lDir = sDirImporter.split( os.sep )
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
  ##! Skip subrpos if explicitly asked.
  if '.sitevcs_noroot' in lContent :
    continue
  if set( [ '.svn', '.hg', '.git', '.sitevcs_root' ] ) & set( lContent ) :
    break
else :
  root = ""

if root :
  site.addsitedir( root )

