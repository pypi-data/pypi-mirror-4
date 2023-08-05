## Script (Python) "getEventDictMMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=event, type='C', sDTS=None, eDTS=None, dayID=None, eWTS=None, mMonth=None, vDict=None, nummons=None
##title=Get dictionary of Event info for Multimonth view
##
"""
returns a dictionary of useful objects for Events for the MultiMonth view  

modified for CalendarX 0.6.4 to fix jsCrossoverFlag bug where events crossing over to a later month not shown cause problems
   NOTE: rollover highlighting extends only one extra month, not for all months in a multiple month view... few monitors are that tall, so I'm not going to worry about it right now, if ever.
Released under the GPL (see LICENSE.txt)
event types: 
   'C' for continuing event (above main calendar view)
   'E' for normal event (in main calendar view)
dayID only submitted with 'E' events
"""
request = container.REQUEST

#get from Property Sheets (true or false right now)
ampm = context.getCXAttribute('hoursDisplay') == '12ampm'

#calculate these DateTimes and related useful objects
eventstart = DateTime(str(event.start))
eventend = DateTime(str(event.end))
if vDict == None:
    startDateToShow = sDTS
    endDateToShow = eDTS
    howManyWeeksToShow = eWTS
else:
    startDateToShow = vDict['startDateToShowList'][mMonth]
    endDateToShow = vDict['endDateToShowList'][mMonth]
    howManyWeeksToShow = vDict['weeksInMonthToShowList'][mMonth]

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
#special eday: if ends at midnight, back it up one day
edaymidnight = str((eventend-1).day())



#calculate jsStart and jsEnd: integer range of cells in view for highlighting
if type == 'C':    #FOR CONTINUING EVENTS
    howManyDays = context.getNumOfDays(startDateToShow, eventend)
    jsStart  = 0
    lastDayOfMonthToShow = startDateToShow + (7*howManyWeeksToShow)
  #FIX too many days called for continuing events running more than all week 
    jsEndIfAllMonth = 7*howManyWeeksToShow
  #the following test() is for events ending ON THE HOUR AT MIDNIGHT, so the highlighting doesn't spill over into the next day upon rollover 
    jsEndIfNotAllMonth = test((eventend.hour() == 0) and (eventend.minute() == 0), 0 + howManyDays, 0 + howManyDays + 1)
    jsEnd = test(jsEndIfNotAllMonth < jsEndIfAllMonth, jsEndIfNotAllMonth, jsEndIfAllMonth)
  #test() to make sure End is not prior to Start
    jsEnd = test(jsEnd < jsStart, jsStart, jsEnd)
  #generate the eventstring
    eventstring = '<strong>'+eventtitle+'</strong> (start: '+stime+' - '+smonth+' '+sday+', '+syear+' | end: '+etime+' - '+emonth+' '+eday+', '+eyear+')'

  #only making rollovers go into the first month for now.
    jsArray = [jsStart,jsEnd]    


#calculate jsStart and jsEnd: integer range of cells in view for highlighting
if type == 'E':    #FOR EVENTS IN THE REGULAR CALENDAR TABLE (not continuing event)
    howManyDays = context.getNumOfDays(eventstart, eventend)
#in order to get showEventsOnlyAtStart to work, we:
# 1. set jsStart to dayID of the first day of the event WRT sDTS
# 2. set jsEnd to the last day of the event.  
    jsStart = 1+context.getNumOfDays(startDateToShow, eventstart)
    jsEnd = jsStart + howManyDays;
  #FIX too many days called for continuing events running more than all month 
    jsEndIfAllMonth = 7*howManyWeeksToShow
  #the following test() is for events ending ON THE HOUR AT MIDNIGHT, so the highlighting doesn't spill over into the next day upon rollover 
    jsEndIfNotAllMonth = test((eventend.hour() == 0) and (eventend.minute() == 0), jsEnd - 1, jsEnd)
    jsEnd = test(jsEndIfNotAllMonth < jsEndIfAllMonth, jsEndIfNotAllMonth, jsEndIfAllMonth)
   #set a flag if we need to carry rollovers into the following months (fixed in 0.6.4 for event crossing into an extra month beyond nummonths)
#    jsCrossoverFlag = test(jsEndIfNotAllMonth > jsEndIfAllMonth and mMonth < 2, 1, 0)
#    jsCrossoverFlag = test((jsEndIfNotAllMonth > jsEndIfAllMonth and mMonth < 2) or (eventstart.month() != eventend.month()), 1, 0)
    jsCrossoverFlag = test((jsEndIfNotAllMonth > jsEndIfAllMonth and mMonth < 2) or (eventstart.month() != eventend.month()) and mMonth+1 < nummons, 1, 0)

  #test() to make sure End is not prior to Start
    jsEnd = test(jsEnd < jsStart, jsStart, jsEnd)
    jsArray = []
#    for i in range(jsStart,jsEnd+1):
#        jsArray.append(mMonth*1000+i)
    jsArray = [mMonth*1000+jsStart,mMonth*1000+jsEnd]    

### For Crossover Events: events crossing month boundaries may need additional start/end array pairs
    if jsCrossoverFlag:
        jsStart2 = 1+(mMonth+1)*1000
      #daysTooMany = how many dates past the end of the month we need to add
        daysTooMany = jsStart + howManyDays - jsEndIfAllMonth 
        daysTooMany = jsStart + howManyDays - jsEndIfAllMonth 
      #wrong, but testing here...
        jsEnd2 = jsStart2 + daysTooMany
        startDateToShow2 = vDict['startDateToShowList'][mMonth+1]
        jsEnd2 = 1+context.getNumOfDays(startDateToShow2, eventend) + (mMonth+1)*1000
        howManyWeeksToShow2 = vDict['weeksInMonthToShowList'][mMonth+1]
        jsEndIfAllMonth2 = 7*howManyWeeksToShow2 + (mMonth+1)*1000
        jsEndIfNotAllMonth2 = test((eventend.hour() == 0) and (eventend.minute() == 0), jsEnd2 - 1, jsEnd2)
        jsEnd2 = test(jsEndIfNotAllMonth2 < jsEndIfAllMonth2, jsEndIfNotAllMonth2, jsEndIfAllMonth2)
        jsArray.append(jsStart2)
        jsArray.append(jsEnd2)



    
  #generate the eventstring (several options depending on whether start/end are on the same day, at the same time, etc.)
    sametime  = (eday == sday) and (emonth == smonth) and (eyear == syear) and (etime == stime)
    sameday = (eday == sday) and (emonth == smonth) and (eyear == syear)
    allday = (eventend.day() == (eventstart+1).day()) and (eventend.TimeMinutes() == eventstart.TimeMinutes() == "00:00")
    multidayendatmidnight = (eventend.Time() == "00:00:00")
#    datestring = (sametime and '%s'%(stime)) or (sameday and '%s - %s'%(stime, etime)) or (allday and '%s %s'%(smonth, sday)) or '%s %s - %s %s'%(smonth, sday, emonth, eday)
    if sametime:
      datestring = '%s'%(stime)
    elif sameday:
      datestring = '%s - %s'%(stime, etime)
    elif allday:
      datestring = '%s %s'%(smonth, sday) 
#      datestring = ''    #uncomment this line, comment out the other one to make AllDay events have a blank datestring
    elif multidayendatmidnight:
      datestring = '%s %s - %s %s'%(smonth, sday, emonth, edaymidnight)
    else:
      datestring = '%s %s - %s %s'%(smonth, sday, emonth, eday)
    eventstring = '<strong>'+eventtitle+'</strong><br/> '+datestring



#marshall all these into a dictionary
emdict = {
         'eventurl':eventurl, 
         'eventstart':eventstart, 
         'eventend':eventend, 
         'jsStart':jsStart, 
         'jsEnd':jsEnd, 
         'jsArray':jsArray, 
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

return emdict

