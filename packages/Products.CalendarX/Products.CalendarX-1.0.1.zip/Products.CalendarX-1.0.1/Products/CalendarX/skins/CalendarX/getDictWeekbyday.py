## Script (Python) "getDictWeekbyday"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get dictionary of weekbyday view info for calendar
##
"""
returns a dictionary of useful objects for the Weekbyday view  

modified for CalendarX 0.6.1(alpha) to speed up query
Released under the GPL (see LICENSE.txt)
"""
request = container.REQUEST

#get the common view dictionary (ALL views must gather this info)
dict = context.getDictCommon('weekbyday')

#retrieve from dict for use in queries
startDate = dict['startDate']
endDate = dict['endDate']
xmy = dict['xmy']
xsub = dict['xsub']
xpub = dict['xpub']
xcrt = dict['xcrt']

#create the continuing events query
#add one second to startDate before querying
startForBefore = DateTime(str(startDate.year())+'/'+str(startDate.month())+'/'+str(startDate.day())+' '+str(startDate.hour())+':01:00')
#continuingEvents = context.getCXEventsBefore(startForBefore, xmy, xsub, xpub, xcrt)

#marshall this view's new parameters into the dictionary
#dict['continuingEvents'] = continuingEvents
dict['startForContinuing'] = startForBefore

return dict

