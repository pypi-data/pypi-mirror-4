## Script (Python) "getStartOfWeek"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime, starthour=0
##title=Get DateTime for start of a week
##
"""
returns a DateTime object for the start of the first day of the week, 
  for use on the calendar month view.  retrieves days from property sheet.

modified for CalendarX 0.4.0(dev) to use context instead of skinobj
Released under the GPL (see LICENSE.txt)
first, try to get these from the calendarx_properties sheet (or whatever it is named)
dowts = integer representing "day of week to start" on for each week
starthour = hour that the calendar begins on
"""
try:
  dowts = int(context.getCXAttribute('dayOfWeekToStart'))
  starthour = int(starthour)

#but if they're not available, set them as default values here
except:
  dowts = 0
  starthour = 0


#set which day of the week has been passed into the function
thisDayInt = dateTime.dow()

#and return midnight of the first day of the week
if thisDayInt < dowts:
    theDay = context.getStartOfDay(dateTime - thisDayInt + dowts - 7,starthour)
else:
    theDay = context.getStartOfDay(dateTime - thisDayInt + dowts,starthour)

return theDay

