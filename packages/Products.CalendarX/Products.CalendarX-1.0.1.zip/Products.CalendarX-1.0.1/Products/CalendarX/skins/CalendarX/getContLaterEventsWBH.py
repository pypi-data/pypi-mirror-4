## Script (Python) "getContLaterEventsWBH"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=evBetween,evBefore,dict,continuing=1
##title=Get a list of continuingEvents or laterEvents for the WeekByHour view
##
"""
returns a list of continuingEvents or laterEvents for the WeekByHour view.  
  This script was created to speed up CalendarX by using a minimum number of 
  catalog calls, and instead parse catalog calls using line comprehensions, 
  which appear to be about 10x faster (according to PTProfiler).  Not profiled 
  with very large numbers of events, however.

new for CalendarX 0.5.0, backported to 0.6.1 (removed CXSheetlist)
mod 0.6.4 to use startForEarly in continuing and later events blocks
Released under the GPL (see LICENSE.txt)

"""

#retrieve from dict for use in queries
weekviewstarthour = dict['viewstarthour']
weekviewendhour = dict['viewendhour']
startDate = dict['startDate']
endDate = dict['endDate']
#earlyHour new in 0.6.4
earlyHour = int(context.getCXAttribute('earlyDayEventHour'))
startForEarly = context.getStartOfDay(startDate,earlyHour)


#create the continuing and noncontinuing events queries
#  (noncontinuing events are events that have a start during the viewable week)
continuingEvents =    []
noncontinuingEvents = []
for dayOfWeek in range(7):
    dayStart = startDate + dayOfWeek
    #added in 0.6.4 dayStartEarly
    dayStartEarly = startForEarly + dayOfWeek
#two line if dayOfWeek commented out in 0.6.4, fixes bug, dunno why it was needed (I'll keep looking)
    if dayOfWeek == 0:
        dayStart = DateTime(str(dayStart.year())+'/'+str(dayStart.month())+'/'+str(dayStart.day())+' '+str(dayStart.hour())+':01:00')
    dayEnd = DateTime(str(dayStart.year())+'/'+str(dayStart.month())+'/'+str(dayStart.day())+' '+str(weekviewendhour - 1)+ ':59:59')
    #daysEventsBetween =   context.getCXEventsBetween(dayStart, dayEnd, xmy, xsub, xcrt, CXsheetlist)
#    daysEventsBetween = [ev for ev in evBetween if (DateTime(str(getattr(ev,'start', ev.start))) >= dayStart and DateTime(str(getattr(ev,'start', ev.start))) <= dayEnd)]

    daysEventsBetween = [ev for ev in evBetween if (DateTime(str(getattr(ev,'start', ev.start))) >= dayStartEarly and DateTime(str(getattr(ev,'end', ev.end))) <= dayStart)]
    noncontinuingEvents += daysEventsBetween
    #daysEventsBefore =    context.getCXEventsBefore(dayStart, xmy, xsub, xcrt, CXsheetlist)
    daysEventsBefore = [ev for ev in evBefore if (DateTime(str(getattr(ev,'start', ev.start))) < dayStart and DateTime(str(getattr(ev,'end', ev.end))) >= dayStart)]
    continuingEvents += daysEventsBefore

continuingEvents =    context.queriesUnique(continuingEvents)
noncontinuingEvents = context.queriesUnique(noncontinuingEvents)
#continuingEvents =    context.queriesSubtract(continuingEvents,noncontinuingEvents)
continuingEvents += noncontinuingEvents
context.listSortByStart(continuingEvents)

if continuing:
    return continuingEvents


#create a laterthan events query
#make sure that these events are not also showing up in other categories above
laterEvents =    []
for dayOfWeek in range(7):
    dayStart = startDate + dayOfWeek
    if weekviewendhour == 24:
        eveStart = DateTime(str(dayStart.year())+'/'+str(dayStart.month())+'/'+str(dayStart.day())+' '+str(weekviewendhour-1)+ ':59:59')
    else:
        eveStart = DateTime(str(dayStart.year())+'/'+str(dayStart.month())+'/'+str(dayStart.day())+' '+str(weekviewendhour)+ ':00:00')
    eveEnd = startDate + 1 + dayOfWeek
#    eveEventsBetween = context.getCXEventsBetween(eveStart, eveEnd, xmy, xsub, xcrt, CXsheetlist)
    eveEventsBetween = [ev for ev in evBetween if (DateTime(str(getattr(ev,'start', ev.start))) >= eveStart and DateTime(str(getattr(ev,'start', ev.start))) <= eveEnd)]
    laterEvents += eveEventsBetween

laterEvents =    context.queriesUnique(laterEvents)
laterEvents =    context.queriesSubtract(laterEvents,continuingEvents)
laterEvents =    context.queriesSubtract(laterEvents,noncontinuingEvents)

return laterEvents

