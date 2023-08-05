## Script (Python) "getEndOfMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime
##title=Get DateTime for end of a month
##
"""
returns a DateTime object for one second before midnight on last day of the Month  

mod by lupa, CalendarX 0.2.8(alpha)
Released under the GPL (see LICENSE.txt)
"""
mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
month = dateTime.month()
return DateTime(str(dateTime.year())+'/'+str(month)+'/'+ str(mdays[month] + (month == 2 and dateTime.isLeapYear()))+' 11:59:59PM')
