## Script (Python) "getNumOfHours"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start, end, starthour=0, endhour=24
##title=Get calendar hours from start to event
##
"""
returns integer number of hours from start of calendar to event.  works for 
  weekbyhour or day view.

mod by lupa, CalendarX 0.2.7 to fix bugs, use timeTime(), list comprehensions
Released under the GPL (see LICENSE.txt)
start = start of calendar week or start of calendar day
end = event time
starthour, endhour refer to start, end of viewable calendar day.
"""

#view hours if in parameters
try: viewstarthour = int(starthour)
except TypeError: viewstarthour = 0
try: viewendhour = int(endhour)
except TypeError: viewendhour = 24


#cheaper: no DateTime conversions needed, but get the real hours between start and end
if viewstarthour == 0 and viewendhour == 24:
    hours = int( (end.timeTime() - start.timeTime()) / 3600 )

#uses DateTime conversion to test inside view hours
else:
    #use bools as heaviside (boxcar) fn
    # i.e., counts if hour is viewable, doesn't count if outside view hours range.
    shour = int(start.timeTime()/60/60)
    ehour = int(end.timeTime()/60/60)
    #use a list comprehension to loop through the hours, count how many are "in" the view.
    hours = len([1 for hr in range(shour,ehour) if viewstarthour <= DateTime(hr*60*60).hour() < viewendhour])

return hours
