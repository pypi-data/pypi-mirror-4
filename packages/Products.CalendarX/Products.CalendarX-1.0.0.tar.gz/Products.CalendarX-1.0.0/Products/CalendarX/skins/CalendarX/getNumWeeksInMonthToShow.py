## Script (Python) "getNumWeeksInMonthToShow"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime
##title=Get number of weeks of a month visible on calendar
##
"""
returns an int number of weeks showing in a Month view showing on the calendar 
  for any given DateTime object (num in that month)(from 4 to 6 weeks possible).

created for CalendarX 0.6.1(alpha) because it helps clean things up
Released under the GPL (see LICENSE.txt)
"""
currentDate = dateTime
endDate = context.getEndOfMonth(dateTime)
startDateToShow = context.getStartOfMonthToShow(dateTime)

#calculate weeks in view
endDateToShow = context.getEndOfDay(startDateToShow + 42 - 1)
weeksToShow = 6
#test for four week month
isFourWeekFebruary = ((currentDate.month() == 2) and ((startDateToShow+28).month() == 3))
if isFourWeekFebruary:
    endDateToShow = context.getEndOfDay(startDateToShow + 28 - 1)
    weeksToShow = 4
#test for five week month
elif endDate <= (startDateToShow + 35) :
    endDateToShow = context.getEndOfDay(startDateToShow + 35 - 1)
    weeksToShow = 5

return weeksToShow

