## Script (Python) "getEndOfWeek"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime, endhour=24
##title=Get DateTime for end of a week
##
"""
returns a DateTime of the last second of the day of the end of the calendar week.

modified for CalendarX 0.4.0(dev) to use context instead of skinobj
Released under the GPL (see LICENSE.txt)
first, try to get these from the calendar properties sheet 
dowts = integer representing "day of week to start" on for each week
"""
try:
  dowts = int(context.getCXAttribute('dayOfWeekToStart'))
#  dayList = context.getCXAttribute('weekdayNames')

#but if they're not available, set them as default values here
except:
  dowts = 0
#  dayList =  ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']


#set which day of the week has been passed into the function
thisDayInt = dateTime.dow()

#and return midnight of the first day of the week
if thisDayInt < dowts:
    theDay = context.getEndOfDay(dateTime - thisDayInt + dowts + 6 - 7,endhour)
else:
    theDay = context.getEndOfDay(dateTime - thisDayInt + dowts + 6,endhour)

return theDay

