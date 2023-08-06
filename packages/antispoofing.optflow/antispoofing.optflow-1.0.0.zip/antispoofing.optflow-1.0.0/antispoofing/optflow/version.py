#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 22 Feb 2013 15:59:16 CET 

"""Returns the currently compiled version number"""

__version__ = __import__('pkg_resources').get_distribution('antispoofing.optflow').version
