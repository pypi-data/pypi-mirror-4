## Script (Python) "getStartOfMonthToShow"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime
##title=Get DateTime for start of a month visible on calendar
##
"""
returns a DateTime for the first of the Month view showing on the calendar 
  (end of the previous month, usually).

modified for CalendarX 0.4.0(dev) to use context instead of skinobj
Released under the GPL (see LICENSE.txt)
first, try to get these from the calendarx_properties sheet (or whatever it is named)
dowts = integer representing "day of week to start" on for each week
"""
try:
  dowts = int(context.getCXAttribute('dayOfWeekToStart'))
#but if they're not available, set them as default values here
except:
  dowts = 0

#set a DateTime object for the first day of the month
monthStart = context.getStartOfMonth(dateTime)

#calculate the day of the week int for the monthStart
monthStartDayInt = monthStart.dow()

#try this one (usually is right)
maybeDay = monthStart - monthStartDayInt + dowts

#test maybeDay against monthStart, and back up a week if too high
if maybeDay > monthStart:
  maybeDay = maybeDay - 7

#return the DateTime of the day the calendar should start on
return maybeDay

