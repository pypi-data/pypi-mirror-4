## Script (Python) "getDictWeekbyhour"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get dictionary of weekbyhour view info for calendar
##
"""
returns a dictionary of useful objects for the Weekbyhour view  

modified for CalendarX-0.6.4 to fix latelate and early events
Released under the GPL (see LICENSE.txt)
"""
request = container.REQUEST

#get the common view dictionary (ALL views must gather this info)
dict = context.getDictCommon('weekbyhour')

#retrieve from dict for use in queries
weekviewstarthour = dict['viewstarthour']
weekviewendhour = dict['viewendhour']
startDate = dict['startDate']
endDate = dict['endDate']
xmy = dict['xmy']
xsub = dict['xsub']
xpub = dict['xpub']
xcrt = dict['xcrt']


# added in 0.6.4
earlyHour = int(context.getCXAttribute('earlyDayEventHour'))
stForQuery = context.getStartOfWeek(startDate)
endweek = context.getEndOfWeek(endDate)
endplus = endweek + 1
if earlyHour > 0:
    enForQuery = DateTime(str(endplus.year())+'/'+str(endplus.month())+'/'+str(endplus.day())+' '+str(earlyHour)+':00:00')
else:
    enForQuery = endweek




#marshall this view's new parameters into the dictionary
dict['weekviewstarthour'] = weekviewstarthour
dict['weekviewendhour'] = weekviewendhour
dict['stForQuery'] = stForQuery 
dict['enForQuery'] = enForQuery 


return dict

