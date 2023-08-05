## Script (Python) "getDictMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get dictionary of month view info for calendar
##
"""
returns a dictionary of useful objects for the Month view  

modified for CalendarX 0.6.4 to fix startForContinuing time bug
Released under the GPL (see LICENSE.txt)
"""
request = container.REQUEST

#get dowts from skin, int representing "day of week to start" on for each week
try: dowts = int(context.getCXAttribute('dayOfWeekToStart'))
except AttributeError: dowts = 0


#get the common view dictionary (ALL views must gather this info)
dict = context.getDictCommon('month')

#retrieve from dict for use in queries
startDate = dict['startDate']
endDate = dict['endDate']
currentDate = dict['currentDate']
xmy = dict['xmy']
xsub = dict['xsub']
xpub = dict['xpub']
xcrt = dict['xcrt']

#calculate start of month to show in view (not usually first of the month)
monthStartDayInt = startDate.dow()                 #calculate the day of the week int
maybeDay = startDate - monthStartDayInt + dowts    #try this one (usually is right)
if maybeDay > startDate:
  maybeDay = maybeDay - 7                          #test against monthStart, and back up a week if too high
startDateToShow = maybeDay

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




#create the continuing events query
#add one minute to startDateToShow before querying
#if showOnlyEventsInMonth property is True, then use startDate, not startDateToShow.
inMonth = context.getCXAttribute('showOnlyEventsInMonth')
if inMonth:
    st = startDate
else:
    st = startDateToShow
startForBefore = DateTime(str(st.year())+'/'+str(st.month())+'/'+str(st.day())+' '+str(st.hour())+':01:00')
startForContinuing = st


#marshall this views' new parameters into the dictionary
dict['startDateToShow'] = startDateToShow 
dict['endDateToShow'] = endDateToShow 
dict['weeksToShow'] = weeksToShow
dict['startForContinuing'] = startForContinuing 

return dict

