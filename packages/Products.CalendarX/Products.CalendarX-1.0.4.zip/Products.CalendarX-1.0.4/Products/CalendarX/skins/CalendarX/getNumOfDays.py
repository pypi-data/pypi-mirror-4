## Script (Python) "getNumOfDays"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start, end, daysordates='dates'
##title=Returns the number of dates or days between two DateTime objects
##
"""
returns an int for number of days or dates between start and end. 
 a "day" is 24 hours, a "date" is calendar day (midnight) 

modified for CalendarX 0.6.3 to correct some comments (no code changes)
Released under the GPL (see LICENSE.txt)
"""
#convert to seconds
endsec = end.timeTime()
startsec = start.timeTime()
startdatesec = context.getStartOfDay(start).timeTime()
enddatesec = context.getStartOfDay(end).timeTime()

#make a correction for Daylight Savings Time changes (DSTsec) 
#if the Spring, then add an hour (DSTsec = 3600)
#if the Fall, then subtract an hour (DSTsec = -3600)
numsec24hrs = 60*60*24  #how many in a 24hr period
secondsinthesedays = enddatesec - startdatesec
overunder = int((numsec24hrs + secondsinthesedays) % numsec24hrs )
DSTsec = 0
if overunder == 3600:
    DSTsec = -3600
if overunder == 82800:
    DSTsec = 3600

#calculates the number of 24 hour days between start and end
#   e.g.  2004/03/12 23:00  to  2004/03/13 03:00 == 0
dayDiff = int((endsec - startsec + DSTsec)/numsec24hrs)

#calculates the number of calendar dates (day numbers) between start and end
#   e.g.  2004/03/12 23:00  to  2004/03/13 03:00 == 1
dateDiff = int((enddatesec - startdatesec + DSTsec)/numsec24hrs)


if daysordates == 'days':
    return dayDiff
else:
    return dateDiff
