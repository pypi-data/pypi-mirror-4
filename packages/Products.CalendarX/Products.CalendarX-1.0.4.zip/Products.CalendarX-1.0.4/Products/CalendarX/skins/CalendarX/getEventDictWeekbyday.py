## Script (Python) "getEventDictWeekbyday"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=event, type, dayID, cDate
##title=Get dictionary of Event info for day view
##
"""
returns a dictionary of useful objects for Events for the Weekbyday view

modified for CalendarX 0.4.8 for untitled events
Released under the GPL (see LICENSE.txt)
event types:
   'C' for continuing event (above main calendar view)
   'E' for normal event (in main calendar view)
hourID only submitted with 'E' events
"""
request = container.REQUEST

#get from Property Sheets (true or false right now)
ampm = context.getCXAttribute('hoursDisplay') == '12ampm'
weekviewstarthour = int(context.getCXAttribute('dayViewStartHour'))
weekviewendhour = int(context.getCXAttribute('dayViewEndHour'))

#get currentDate from passed cDate, not from request or default
currentDate = cDate


#calculate these DateTimes and related useful objects
startDate = context.getStartOfWeek(currentDate,weekviewstarthour)
endDate = context.getEndOfWeek(currentDate,weekviewendhour)
nextDate = (currentDate + 7).Date()
prevDate = (currentDate - 7).Date()
eventstart = DateTime(str(event.start))
eventend = DateTime(str(event.end))

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
    howManyDays = context.getNumOfDays(startDate, eventend)
    jsStart = dayID
    jsEnd = dayID + howManyDays
    jsEndIfAllWeek = 7
  #the following test() is for events ending ON THE HOUR AT MIDNIGHT, so the highlighting doesn't spill over into the next day upon rollover
    jsEndIfNotAllWeek = test((eventend.hour() == 0) and (eventend.minute() == 0), jsEnd, jsEnd + 1)
    jsEnd = test(jsEndIfNotAllWeek < jsEndIfAllWeek, jsEndIfNotAllWeek, jsEndIfAllWeek)
  #test() to make sure End is not prior to Start
    jsEnd = test(jsEnd < jsStart, jsStart, jsEnd)
  #generate the eventstring
    eventstring = '<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'

#calculate jsStart and jsEnd: integer range of cells in view for hightlighting
if type == 'E':    #FOR EVENTS IN THE REGULAR DAY by hour TABLE
    howManyDays = context.getNumOfDays(eventstart, eventend, daysordates='dates')
    jsStart = dayID
    jsEnd = dayID + howManyDays
  #FIX too many days called for continuing events running more than all week
    jsEndIfAllWeek = 7
  #the following test() is for events ending ON THE STROKE OF MIDNIGHT, so the highlighting doesn't spill over into the next day upon rollover
    jsEndIfNotAllWeek = test((eventend.hour() == 0) and (eventend.minute() == 0), jsEnd - 1, jsEnd)
    jsEnd = test(jsEndIfNotAllWeek < jsEndIfAllWeek, jsEndIfNotAllWeek, jsEndIfAllWeek)
  #test() to make sure End is not prior to Start
    jsEnd = test(jsEnd < jsStart, jsStart, jsEnd)
  #generate the eventstring
    eventstring = '<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'




#marshall all these into a dictionary
ewbddict = {
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

return ewbddict

