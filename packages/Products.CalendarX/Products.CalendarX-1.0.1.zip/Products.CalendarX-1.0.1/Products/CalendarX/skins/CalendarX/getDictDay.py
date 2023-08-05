## Script (Python) "getDictDay"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get dictionary of day view info for calendar
##
"""
returns a dictionary of useful objects for the Day view  

modified for CalendarX 0.6.4(RC1) added startForEarly, changed eveEnd
  datetime object to one minute before startForEarly.
Released under the GPL (see LICENSE.txt)
"""
request = container.REQUEST

#get the common view dictionary (ALL views must gather this info)
dict = context.getDictCommon('day')

#retrieve from dict for use in queries
dayviewstarthour = dict['viewstarthour']
dayviewendhour = dict['viewendhour']
startDate = dict['startDate']
endDate = dict['endDate']
xmy = dict['xmy']
xsub = dict['xsub']
xpub = dict['xpub']
xcrt = dict['xcrt']



#prepare for the continuing events query
startForBefore = startDate 
earlyHour = int(context.getCXAttribute('earlyDayEventHour'))
startForEarly = context.getStartOfDay(startForBefore,earlyHour)

#prepare for the laterthan events query
eveStart = endDate
#0.6.4+: now eveEnd equals one minute before startForEarly of next day
eveEnd = startForEarly + 1 -(1.0/24.0/60.0) 

#marshall this views new parameters into the dictionary
dict['dayviewstarthour'] = dayviewstarthour
dict['dayviewendhour'] = dayviewendhour
dict['startForContinuing'] = startForBefore 
dict['startForEarly'] = startForEarly
dict['eveStart'] = eveStart
dict['eveEnd'] = eveEnd

return dict

