## Script (Python) "getDictCommon"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=viewname, cDate=None
##title=Get dictionary of info common to all views
##
"""
returns a dictionary of useful objects for the calendar views

modified for CalendarX 0.9.1 to improve subcalendar usage and fix View All bug
Released under the GPL (see LICENSE.txt)
viewname = string name of the view page template
IMPORTANT:  If you add a new view to your calendar, it must be added in here.  See code.
"""
request = container.REQUEST

#get from Property Sheets (true or false right now)
ampm = context.getCXAttribute('hoursDisplay') == '12ampm'
viewstarthour = int(context.getCXAttribute('dayViewStartHour'))
viewendhour = int(context.getCXAttribute('dayViewEndHour'))
nummonths = int(context.getCXAttribute('numMonthsForMultiMonthView'))


#get from request (querystring), or default
try: xmy = request.xmy
except AttributeError: xmy = '0'
try: 
# (mod 0.6.1) make 'ALL' disappear so it doesn't override other subjects anymore
    xsub = request.xsub
    xsub = context.makeCSV(xsub)
    xsub = str(xsub)
    xsub = string.split(xsub, ",") 
    if 'ALL' in xsub and len(xsub) > 1:
        xsub.remove('ALL')
    xsub = ','.join(xsub)
except AttributeError: xsub = 'ALL'
# (mod 0.9.1) if xsubALL is present and == 'ALL', then xsub='ALL'
if hasattr(request,'xsubALL'):  
    xsubALL = request.xsubALL
    if xsubALL == 'ALL':
        xsub = 'ALL'

if hasattr(request,'xpub'):  
    xpub = request.xpub
else:
    xpub = '1'
if hasattr(request,'xcrt'):  
    xcrt = request.xcrt
else:
    xcrt = '0'

#first set currentDate from the request, then override it from the Jump widget, if available
if hasattr(request,'currentDate'):  
    currentDate = DateTime(request.currentDate)
else:
    currentDate = DateTime()
if hasattr(request,'jumpyear'):
    try:
        year = int(request.jumpyear)
        month = int(request.jumpmonth)
        day = int(request.jumpday)
        currentDate = DateTime(year,month,day)
    except:
        currentDate = DateTime()

"""
 IMPORTANT: add a section here for each view in your calendar 
"""
startDate = ''
endDate = ''
startDateList = []
endDateList = []
startDateToShowList = []
endDateToShowList = []
weeksInMonthToShowList = []

if viewname == 'month':
    startDate = context.getStartOfMonth(currentDate)
    endDate = context.getEndOfMonth(currentDate)
    nextDate = (endDate + 1).Date()
    prevDate = (startDate - 1).Date()
    prevstring = 'previous month'
    nextstring = 'next month'
    currentstring = str(currentDate.Month())+' '+str(currentDate.year())
if viewname == 'weekbyday':
    startDate = context.getStartOfWeek(currentDate)
    endDate = context.getEndOfWeek(currentDate)
    nextDate = (currentDate + 7).Date()
    prevDate = (currentDate - 7).Date()
    prevstring = 'previous week'
    nextstring = 'next week'
    currentstring = str(startDate.Month())+' '+str(startDate.day())+', '+str(startDate.year())+' - '+str(endDate.Month())+' '+str(endDate.day())+', '+str(endDate.year())
if viewname == 'day':
    startDate = context.getStartOfDay(currentDate,viewstarthour)
    endDate = context.getEndOfDay(currentDate,viewendhour)
    nextDate = (currentDate + 1).Date()
    prevDate = (currentDate - 1).Date()
    prevstring = 'previous day'
    nextstring = 'next day'
    currentstring = str(startDate.Month())+' '+str(startDate.day())+', '+str(startDate.year())+' ('+str(currentDate.Day())+')' 
if viewname == 'weekbyhour':
    startDate = context.getStartOfWeek(currentDate,viewstarthour)
    endDate = context.getEndOfWeek(currentDate,viewendhour)
    nextDate = (currentDate + 7).Date()
    prevDate = (currentDate - 7).Date()
    prevstring = 'previous week'
    nextstring = 'next week'
    currentstring = str(startDate.Month())+' '+str(startDate.day())+', '+str(startDate.year())+' - '+str(endDate.Month())+' '+str(endDate.day())+', '+str(endDate.year())
if viewname == 'multimonth':
    startDate = context.getStartOfMonth(currentDate)
    endDate = context.getEndOfMonth(currentDate)
    nextDate = (endDate + 1).Date()
    prevDate = (startDate - 1).Date()
    prevstring = 'previous month'
    nextstring = 'next month'
    currentstring = str(currentDate.Month())+' '+str(currentDate.year())
    for monthnum in range(nummonths):
        midmonth = DateTime(str(currentDate.year())+'/'+str(currentDate.month())+'/15')
        midmonth += monthnum*30
        startDate = context.getStartOfMonth(midmonth)
        startDateToShow = context.getStartOfMonthToShow(midmonth)
        weeksInMonthToShow = context.getNumWeeksInMonthToShow(midmonth)
        endDate = context.getEndOfMonth(midmonth)
        endDateToShow = context.getEndOfDay(startDateToShow + (7*weeksInMonthToShow) - 1)
        startDateList.append(startDate)
        endDateList.append(endDate)
        startDateToShowList.append(startDateToShow)
        endDateToShowList.append(endDateToShow)
        weeksInMonthToShowList.append(weeksInMonthToShow)


#if a subCalendar, add these.
if context.getCXAttribute('isSubCalendar'):
    subcalname = context.absolute_url().split('/')[-1].upper()
#    subcalname = context.absolute_url().split('/')[-2]
#    scals = context.getCXAttribute('listOfSubCalendars')
#    scalnames = context.getCXAttribute('listOfSubjectTitles')
#    subcalname = context.matchinlists(scals,scalnames,subcalname)
else:
    subcalname = ''
othername = context.getCXAttribute('nameOfSubCalendar')
if othername and context.getCXAttribute('isSubCalendar'):
    subcalname = othername



#need these URLs for macros and querystrings
url =               context.absolute_url()
strDate =           currentDate.Date();
urlThis =           url+'/'+viewname+'?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlNext =           url+'/'+viewname+'?currentDate='+nextDate+'&xmy='+xmy+'&xsub='+xsub
urlPrev =           url+'/'+viewname+'?currentDate='+prevDate+'&xmy='+xmy+'&xsub='+xsub
urlWeek =           url+'/weekbyday?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlWeek2 =          url+'/weekbyhour?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
#ADDED FOR 0.6.1
urlWeek3 =          url+'/week?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlWeekend =        url+'/weekend?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlHelp =           url+'/helpcx?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlDay =            url+'/day?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlDaylist =        url+'/daylist?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlMonth =          url+'/month?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlMonth2 =          url+'/multimonth?currentDate='+strDate+'&xmy='+xmy+'&xsub='+xsub
urlMinusXsub =      url+'/'+viewname+'?currentDate='+strDate+'&xmy='+xmy
urlAllEventsChange =     test(xmy == '1', url + '/'+viewname+'?currentDate=' + strDate + '&xmy=0&xsub=' + xsub, url + '/'+viewname+'?currentDate=' + strDate + '&xmy=1&xsub=' + xsub)
allEventsChangeString =  test(xmy == '1', 'label_sublinks_private','label_sublinks_public')




#marshall all these into a dictionary
cdict = {
         'ampm':ampm, 
         'viewstarthour':viewstarthour, 
         'viewendhour':viewendhour, 
         'xmy':xmy, 
         'xsub':xsub, 
         'xpub':xpub, 
         'xcrt':xcrt, 
         'currentDate':currentDate, 
         'startDate':startDate, 
         'endDate':endDate, 
         'startDateList':startDateList, 
         'endDateList':endDateList, 
         'startDateToShowList':startDateToShowList, 
         'endDateToShowList':endDateToShowList, 
         'weeksInMonthToShowList':weeksInMonthToShowList,
         'nummonths':nummonths, 
         'nextDate':nextDate, 
         'prevDate':prevDate, 
         'prevstring':prevstring, 
         'nextstring':nextstring, 
         'currentstring':currentstring, 
         'subcalname':subcalname, 
         'urlThis':urlThis, 
         'urlNext':urlNext, 
         'urlPrev':urlPrev, 
         'urlWeek':urlWeek, 
         'urlWeek2':urlWeek2, 
         'urlWeek3':urlWeek3, 
         'urlWeekend':urlWeekend, 
         'urlHelp':urlHelp, 
         'urlDay':urlDay, 
         'urlDaylist':urlDaylist, 
         'urlMonth':urlMonth, 
         'urlMonth2':urlMonth2, 
         'urlMinusXsub':urlMinusXsub, 
         'urlAllEventsChange':urlAllEventsChange, 
         'allEventsChangeString':allEventsChangeString, 
        }

return cdict

