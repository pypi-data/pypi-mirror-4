## Script (Python) "getDictMultiMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=startmonth=1, nummonths=1
##title=Get dictionary of multiple months view info for calendar
##
"""
returns a dictionary of useful objects for the Month view  

modified for CalendarX 0.6.2 for just a bit of cleanup
Released under the GPL (see LICENSE.txt)
"""
request = container.REQUEST

#get dowts from skin, int representing "day of week to start" on for each week
try: dowts = int(context.getCXAttribute('dayOfWeekToStart'))
except AttributeError: dowts = 0


#get the common view dictionary (ALL views must gather this info)
dict = context.getDictCommon(viewname='multimonth')

#retrieve from dict for use in queries
startDate = dict['startDate']
endDate = dict['endDate']
startDateList = dict['startDateList']
endDateList = dict['endDateList']
startDateToShowList = dict['startDateToShowList']
endDateToShowList = dict['endDateToShowList']
weeksInMonthToShowList = dict['weeksInMonthToShowList']
currentDate = dict['currentDate']
xmy = dict['xmy']
xsub = dict['xsub']
xpub = dict['xpub']
xcrt = dict['xcrt']

##calculate start of month to show in view (not usually first of the month)
#monthStartDayInt = startDate.dow()                 #calculate the day of the week int
#maybeDay = startDate - monthStartDayInt + dowts    #try this one (usually is right)
#if maybeDay > startDate:
#  maybeDay = maybeDay - 7                          #test against monthStart, and back up a week if too high
#startDateToShow = maybeDay
#startDateToShowList = []
#startDateToShowList.append(startDateToShow)

##calculate weeks in view
#endDateToShow = context.getEndOfDay(startDateToShow + 42 - 1)
#weeksToShow = 6
##test for four week month
#isFourWeekFebruary = ((currentDate.month() == 2) and ((startDateToShow+28).month() == 3))
#if isFourWeekFebruary:
#    endDateToShow = context.getEndOfDay(startDateToShow + 28 - 1)
#    weeksToShow = 4
##test for five week month
#elif endDate <= (startDateToShow + 35) :
#    endDateToShow = context.getEndOfDay(startDateToShow + 35 - 1)
#    weeksToShow = 5

#endDateToShowList = []
#endDateToShowList.append(endDateToShow)
#weeksToShowList = []
#weeksToShowList.append(weeksToShow)



#create the continuing events query
#add one minute to startDateToShow before querying
#if showOnlyEventsInMonth property is True, then use startDate, not startDateToShow.
startDateToShow = context.getStartOfMonthToShow(startDate)
inMonth = context.getCXAttribute('showOnlyEventsInMonth')
if inMonth:
    st = startDateList[0]
else:
    st = startDateToShowList[0]
startForBefore = st + (1.0/24.0/60.0)


#optional mod: use startDate instead of startDateToShow and filter for events starting on startForBefore
#  => yields a calendar with events only for the chosen month, not before and after events
#startForBefore = DateTime(str(startDate.year())+'/'+str(startDate.month())+'/'+str(startDate.day())+' '+str(startDate.hour())+':01:00')
#startForBeforeMidnight = DateTime(str(startDate.year())+'/'+str(startDate.month())+'/'+str(startDate.day())+' '+str(startDate.hour())+':00:00')
#continuingEvents = context.getCXEventsBefore(startForBefore, xmy, xsub, xpub, xcrt)
#continuingEvents = [ev for ev in continuingEvents if ev.start < startForBeforeMidnight];



#marshall this view's new parameters into the dictionary
dict['startDateToShowList'] = startDateToShowList 
dict['endDateToShowList'] = endDateToShowList 
dict['weeksInMonthToShowList'] = weeksInMonthToShowList

#new or mod in 0.6.1
#dict['continuingEvents'] = continuingEvents
dict['startForContinuing'] = startForBefore 

return dict

