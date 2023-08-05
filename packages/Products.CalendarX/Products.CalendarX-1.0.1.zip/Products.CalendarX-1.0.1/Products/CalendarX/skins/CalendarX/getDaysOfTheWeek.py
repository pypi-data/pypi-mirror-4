## Script (Python) "getDaysOfTheWeek"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get the days of the week in proper order for display
##
"""
returns a list of the names of the seven days of the week, in a proper order 
  for use on the calendar month view.  

modified for CalendarX 0.4.0(dev) to use context instead of skinobj
Released under the GPL (see LICENSE.txt)
first, try to get these from the calendar_properties sheet 
dowts = integer representing "day of week to start" on for each week
"""
try:
    dowts = int(context.getCXAttribute('dayOfWeekToStart'))
except:
    dowts = 0


dayList = []
seedSunday = DateTime('2004/07/25')
for day in range(7):
    theDay = str((seedSunday + day).Day())
    dayList.append(theDay)


#make a new list, adjusting for the dowts
newDayList = []
for d in range(7):
    dayNum = d + dowts
    if dayNum > 6:
      dayNum = dayNum -7
    if dayNum > 6 or dayNum < -7:
      dayNum = 0
    newDayList.append(dayList[dayNum])

return newDayList

