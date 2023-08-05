## Script (Python) "getCXEventsBetween"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start, end, xmy, xsub, xpub, xcrt
##title=Choose means of getting Events starting between dates
##
"""
Chooses which means of querying the catalog for Events between two dates.

created by lupa for CalendarX-0.1.x 
Released under the GPL (see LICENSE.txt)
modified for CalendarX 0.4.0(dev) to use context instead of skinobj
  Switches to the getEventsBetween query that doesn't use AdvancedQuery if 
  selected in the CalendarX property sheet.
"""
#base the query on the value of 'useAdvancedQuery' in calendarx property sheet
if not context.getCXAttribute('useAdvancedQuery'):
    return context.getEventsBetweenZC(start, end, xmy, xsub, xpub, xcrt)
else:
    return context.getEventsBetweenAQ(start, end, xmy, xsub, xpub, xcrt)

