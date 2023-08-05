## Script (Python) "getDaysOfMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dateTime
##title=
##
mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

month = dateTime.month()

return mdays[month] + (month == 2 and dateTime.isLeapYear())
