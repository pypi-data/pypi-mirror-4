## Script (Python) "getEventDictDay"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=event, type='C', periodID=None, cDate=None
##title=Get dictionary of Event info for day view
##
"""
returns a dictionary of useful objects for Events for the Day view

modified for CalendarX-0.6.4 change jsStart to reflect "earlier" event
  highlighting changes.
Released under the GPL (see LICENSE.txt)
event types:
   'C' for continuing event (above main calendar view)
   'E' for normal event (in main calendar view)
   'L' for later event (below main calendar view)
"""
request = container.REQUEST

#get from Property Sheets (true or false right now)
ampm = context.getCXAttribute('hoursDisplay') == '12ampm'
dayviewstarthour = int(context.getCXAttribute('dayViewStartHour'))
dayviewendhour = int(context.getCXAttribute('dayViewEndHour'))
useHalfHours = context.getCXAttribute('useHalfHours')

#get currentDate from passed params, not from request or default (bug in pre 0.6.3)
currentDate = cDate

#calculate these DateTimes and related useful objects
startDate = context.getStartOfDay(currentDate,dayviewstarthour)
endDate = context.getEndOfDay(currentDate,dayviewendhour)
nextDate = (currentDate + 1).Date()
prevDate = (currentDate - 1).Date()
eventstart = DateTime(str(event.start))
eventend = DateTime(str(event.end))
#MODDED FOR 0.6.1
if useHalfHours:
    periodsFactor = 2
else:
    periodsFactor = 1
periodsInDay = (dayviewendhour - dayviewstarthour)*periodsFactor
periodsInView = periodsInDay - 1

#display parameters common to ALL event types
eventurl =  str(event.getURL())+'/view'
eventState = event.review_state
eventtitle = str(event.Title)
if not eventtitle:
    eventtitle = 'untitled'
portaltype = str(event.Type)
syear = str(eventstart.year())
smonth = eventstart.aMonth()
sday = str(eventstart.day())
stime = test(ampm, eventstart.AMPMMinutes(), eventstart.TimeMinutes() + ' h')
eyear = str(eventend.year())
emonth = eventend.aMonth()
eday = str(eventend.day())
etime = test(ampm, eventend.AMPMMinutes(), eventend.TimeMinutes() + ' h')


#calculate jsStart and jsEnd: integer range of cells in view for hightlighting
if type == 'C':    #FOR CONTINUING EVENTS
    howManyPeriods = context.getNumOfPeriods(startDate, eventend, dayviewstarthour, dayviewendhour)
    #0.6.4 change to highlight cEvents cell if an early event (not for actual continuing events)
#    jsStart = dayviewstarthour*periodsFactor + 1   #ONLY highlights the hours below, not the cEvents cell
    jsStart = test(eventend <= startDate,dayviewstarthour*periodsFactor,dayviewstarthour*periodsFactor + 1)

    jsEnd = jsStart + howManyPeriods
    jsEndIfAllDay = jsStart + periodsInView
  #the following test() is for events ending ON THE PERIOD, so they don't spill over into the next period upon rollover.
    if useHalfHours:
        jsEndIfNotAllDay = test(eventend.minute() in [0,30], jsEnd-1, jsEnd)
    else:
        jsEndIfNotAllDay = test(eventend.minute() in [0], jsEnd-1, jsEnd)
    jsEnd = test(jsEndIfNotAllDay < jsEndIfAllDay, jsEndIfNotAllDay, jsEndIfAllDay)
  #test() just to make sure End is not prior to Start; an old test, not sure it is still needed.
    jsEnd = test(jsEnd < jsStart, jsStart, jsEnd)
  #generate the eventstring
    eventstring = '<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'


#calculate jsStart and jsEnd: integer range of cells in view for hightlighting
if type == 'E':    #FOR EVENTS IN THE REGULAR DAY by hour TABLE
    howManyPeriods = context.getNumOfPeriods(eventstart, eventend, dayviewstarthour, dayviewendhour)
    jsStart = periodID
    jsEnd = jsStart + howManyPeriods
    jsEndIfAllDay = dayviewendhour*periodsFactor
  #the following test() is for events ending ON THE PERIOD, so they don't spill over into the next period upon rollover.
    if useHalfHours:
        jsEndIfNotAllDay = test(eventend.minute() in [0,30], jsEnd-1, jsEnd)
    else:
        jsEndIfNotAllDay = test(eventend.minute() in [0], jsEnd-1, jsEnd)
    jsEnd = test(jsEndIfNotAllDay < jsEndIfAllDay, jsEndIfNotAllDay, jsEndIfAllDay)
  #test() to make sure End is not prior to Start
    jsEnd = test(jsEnd < jsStart, jsStart, jsEnd)
  #generate the eventstring
    eventstring = '<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'



#calculate jsStart and jsEnd: integer range of cells in view for hightlighting
if type == 'L':    #FOR LATER EVENTS
    jsStart = dayviewendhour*periodsFactor + 1
    jsEnd = jsStart
  #generate the eventstring
    eventstring = '<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'




#marshall all these into a dictionary
eddict = {
         'eventurl':eventurl,
         'eventstart':eventstart,
         'eventend':eventend,
         'jsStart':jsStart,
         'jsEnd':jsEnd,
         'eventurl':eventurl,
         'eventState':eventState,
         'eventtitle':eventtitle,
         'portaltype':portaltype,
         'syear':syear,
         'smonth':smonth,
         'sday':sday,
         'stime':stime,
         'eyear':eyear,
         'emonth':emonth,
         'eday':eday,
         'etime':etime,
         'eventstring':eventstring,
        }

return eddict

