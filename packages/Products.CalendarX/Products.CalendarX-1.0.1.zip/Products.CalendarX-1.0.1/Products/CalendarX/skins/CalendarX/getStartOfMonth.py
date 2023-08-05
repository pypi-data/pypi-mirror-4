## Script (Python) "getStartOfMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime
##title=Get DateTime for midnight on 1st of the month
##
"""
returns a DateTime object for midnight on 1st day of the Month  

mod by lupa, CalendarX 0.2.8 for year/month/day
Released under the GPL (see LICENSE.txt)
"""
return DateTime(str(dateTime.year())+'/'+str(dateTime.month())+'/01 12:00:00AM')
