## Script (Python) "getStartOfDay"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime, hour=0
##title=Get DateTime for end of day on day view
##
"""
returns a DateTime object for the beginning of the Day view showing on the calendar 
  (defaults to midnight).

added by lupa, CalendarX 0.2.3(dev)
Released under the GPL (see LICENSE.txt)
  allows an hour to be sent as start of "calendar day"
  works for any hour (integer) of the day, from 0-23, otherwise defaults to midnight.
  hour is optional, defaults to midnight if not provided
"""
#dateTime = DateTime(dateTime)   #USE THIS LINE ONLY FOR TESTING WITH DATESTRINGS
try: 
    datestrYMD = str(dateTime.year())+'/'+str(dateTime.month())+'/'+str(dateTime.day())
    hour = int(hour)
    hourstr = ' '+str(hour)+':00:00'
    dT = DateTime(datestrYMD + hourstr)
except:
    datestrYMD = str(dateTime.year())+'/'+str(dateTime.month())+'/'+str(dateTime.day())
    hourstr = ' 12:00:00AM'
    dT = DateTime(datestrYMD + hourstr)

return dT
