#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 06 Mar 2013 18:23:09 CET 

"""Returns the currently compiled version number"""

__version__ = __import__('pkg_resources').get_distribution('xbob.daq').version
