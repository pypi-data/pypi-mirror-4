## Script (Python) "getEventDictWeekbyhour"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=event=None, type='C', periodID=None, cDate=None
##title=Get dictionary of Event info for weekbyhour view
##
"""
returns a dictionary of useful objects for Events for the Weekbyhour view

modified for CalendarX-0.6.4 mod Later events to highlight proper date (matches event start date).
Released under the GPL (see LICENSE.txt)
event types:
   'C' for continuing event (above main calendar view)
   'E' for normal event (in main calendar view)
   'L' for later event (below main calendar view)
hourID only submitted with 'E' events
"""
request = container.REQUEST

#get from Property Sheets (true or false right now)
ampm = context.getCXAttribute('hoursDisplay') == '12ampm'
weekviewstarthour = int(context.getCXAttribute('dayViewStartHour'))
weekviewendhour = int(context.getCXAttribute('dayViewEndHour'))
earlyHour = int(context.getCXAttribute('earlyDayEventHour'))
useHalfHours = context.getCXAttribute('useHalfHours')

#get from passed cDate, no longer from request, or default
currentDate = cDate

#calculate these DateTimes and related useful objects
startDate = context.getStartOfWeek(currentDate,weekviewstarthour)
endDate = context.getEndOfWeek(currentDate,weekviewendhour)
nextDate = (currentDate + 7).Date()
prevDate = (currentDate - 7).Date()
eventstart = DateTime(str(event.start))
eventend = DateTime(str(event.end))
#MODDED FOR 0.6.1
if useHalfHours:
    periodsFactor = 2
else:
    periodsFactor = 1
periodsInDay = (weekviewendhour - weekviewstarthour)*periodsFactor
periodsInView = 7*periodsInDay -1

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


#calculate jsStart and jsEnd: integer range of cells in view for highlighting
if type == 'C':    #FOR CONTINUING EVENTS
    daysTilWeekEnd = context.getNumOfDays(eventstart, startDate+6, daysordates='days')
    daysTilWeekEnd = test(daysTilWeekEnd > 6, 6, daysTilWeekEnd)
    jsStart  = weekviewstarthour*periodsFactor + 1 + (6-daysTilWeekEnd)*periodsInDay
    #0.6.4 change to highlight cEvents cell if an early event (not for actual continuing events)
    isEarly = earlyHour <= eventend.hour() < weekviewstarthour
    jsStart = test(isEarly,weekviewstarthour*periodsFactor,jsStart)
    jsEndIfAllWeek = jsStart + periodsInView
  #datetime at start of viewday that event shows up on (at jsStart)
    dtDayStart = startDate + 6 - daysTilWeekEnd
    periodsToShow = context.getNumOfPeriods(dtDayStart, eventend, weekviewstarthour, weekviewendhour)
    jsEnd = jsStart + periodsToShow
  #then test() for ending ON THE HOUR or HALFHOUR, so events don't spill over into the next period upon rollover.
  #  and test() for ending OFF THE VIEW, so events don't spill over into the next period upon rollover.
    eventEndIsInView = weekviewstarthour <= eventend.hour() < weekviewendhour
    if useHalfHours:
        jsEndIfNotAllWeek = test(eventend.minute() in [0,30] or not eventEndIsInView, jsEnd-1, jsEnd)
    else:
        jsEndIfNotAllWeek = test(eventend.minute() in [0] or not eventEndIsInView, jsEnd-1, jsEnd)
    jsEnd = test(jsEndIfNotAllWeek < jsEndIfAllWeek, jsEndIfNotAllWeek, jsEndIfAllWeek)
  #test() to make sure End is not prior to Start
    jsEnd = test(jsEnd < jsStart, jsStart, jsEnd)
  #generate the eventstring
    eventstring = '<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'



#calculate jsStart and jsEnd: integer range of cells in view for hightlighting
if type == 'E':    #FOR EVENTS IN THE REGULAR WEEKBYHOUR TABLE
    howManyPeriods = context.getNumOfPeriods(eventstart, eventend, weekviewstarthour, weekviewendhour)
    jsStart = periodID
    jsEnd = jsStart + howManyPeriods
    jsEndIfAllWeek = weekviewstarthour*periodsFactor + periodsInView
  #the following test() is for events ending ON THE PERIOD, so they don't spill over into the next period upon rollover.
    if useHalfHours:
        jsEndIfNotAllWeek = test(eventend.minute() in [0,30], jsEnd-1, jsEnd)
    else:
        jsEndIfNotAllWeek = test(eventend.minute() in [0], jsEnd-1, jsEnd)
    jsEnd = test(jsEndIfNotAllWeek < jsEndIfAllWeek, jsEndIfNotAllWeek, jsEndIfAllWeek)
  #test() to make sure End is not prior to Start
    jsEnd = test(jsEnd < jsStart, jsStart, jsEnd)
  #generate the eventstring
    sameday = (eday == sday) and (emonth == smonth) and (eyear == syear)
    datestring = (sameday and '%s - %s'%(stime, etime)) or '%s %s - %s %s'%(smonth, sday, emonth, eday)
    eventstring = '<strong>'+eventtitle+'</strong><br/> '+datestring



#calculate jsStart and jsEnd: integer range of cells in view for hightlighting
#only highlight ONE Day, the day where the event starts (albeit late)
if type == 'L':    #FOR LATER EVENTS
    firstEveOfWeek = endDate - 6
    evesTilEventStart = context.getNumOfDays(firstEveOfWeek, eventstart) + 1
    jsStart = weekviewstarthour*periodsFactor + 1 + periodsInView + evesTilEventStart
  #test for wee hours events, bring them back to the previous day for highlighting
  #0.6.4 change to highlight previous day cell if a late late event (wee hours) AND not first day of the week
    isLateLate = 0 <= eventstart.hour() < earlyHour
    jsStart = test(isLateLate and evesTilEventStart > 1, jsStart-1, jsStart)
    jsEnd = jsStart
  #generate the eventstring
#    eventstring = str(jsStart)+'_'+str(firstEveOfWeek)+'_'+str(evesTilEventStart)+'_'+'<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'
    eventstring = '<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'




#marshall all these into a dictionary
ewbhdict = {
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

return ewbhdict

