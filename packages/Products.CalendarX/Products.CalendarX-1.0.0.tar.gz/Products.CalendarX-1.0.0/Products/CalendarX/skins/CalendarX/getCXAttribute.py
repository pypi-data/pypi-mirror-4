## Script (Python) "getCXAttribute"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=key
##title=key = name of desired attribute
##
"""
Returns an attribute from CalendarX's schema.

mod by lupa for CalendarX-0.9.0(dev)
Released under the GPL (see LICENSE.txt)
key = name of the attribute desired.  REQUIRED.
modified for Archetypes and /plone-3-compatibility branch at the 
  PSU CalendarX Patch Sprint in Dec 2007. thanks folks :-)
"""

return getattr(context, 'get%s%s' % (key[0].upper(), key[1:]))()
