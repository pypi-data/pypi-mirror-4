## Script (Python) "getCXEventsBefore"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start, xmy, xsub, xpub, xcrt, end=None
##title=Choose means of getting Events starting before date
##
"""
Chooses which means of querying the catalog for Events before a given date.

created by lupa for CalendarX-0.1.x 
Released under the GPL (see LICENSE.txt)
modified for CalendarX 0.6.1 to add end as a parameter for faster querying
  Switches to the getEventsBetween query that doesn't use AdvancedQuery if 
  selected in the CalendarX property sheet.
"""
#base the query on the value of 'useAdvancedQuery' in calendarx property sheet
if not context.getCXAttribute('useAdvancedQuery'):
    return context.getEventsBeforeZC(start, xmy, xsub, xpub, xcrt, end)
else:
    return context.getEventsBeforeAQ(start, xmy, xsub, xpub, xcrt, end)

