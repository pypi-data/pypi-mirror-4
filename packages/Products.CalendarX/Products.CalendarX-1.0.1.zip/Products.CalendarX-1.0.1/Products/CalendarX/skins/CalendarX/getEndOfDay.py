## Script (Python) "getEndOfDay"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime, hour=24
##title=Get DateTime for end of day on day view
##
"""
returns a DateTime object for the end of the Day view showing on the calendar 
  (defaults to one second before midnight). Hour range: 1-24.

added by lupa, CalendarX 0.2.3(dev) 
Released under the GPL (see LICENSE.txt)
  Allows an hour to be sent as end of "calendar day", which
  works for any hour (integer) of the day, from 0-23, otherwise defaults to midnight.
  hour is optional, defaults to one second before midnight if not provided
"""
#dateTime = DateTime(dateTime)   #USE THIS LINE ONLY FOR TESTING WITH DATESTRINGS
try: 
    datestrYMD = str(dateTime.year())+'/'+str(dateTime.month())+'/'+str(dateTime.day())
    hour = int(hour)-1 
    if hour >= 0 and hour < 25 :
        hourstr = ' '+str(hour)+':59:59'
    else:
        hourstr = ' 11:59:59PM'
    dT = DateTime(datestrYMD + hourstr)
except:
    datestrYMD = str(dateTime.year())+'/'+str(dateTime.month())+'/'+str(dateTime.day())
    hourstr = ' 11:59:59PM'
    dT = DateTime(datestrYMD + hourstr)

return dT



#return DateTime(str(dateTime.month())+'/'+str(dateTime.day())+'/'+str(dateTime.year())+' 11:59:59PM')
