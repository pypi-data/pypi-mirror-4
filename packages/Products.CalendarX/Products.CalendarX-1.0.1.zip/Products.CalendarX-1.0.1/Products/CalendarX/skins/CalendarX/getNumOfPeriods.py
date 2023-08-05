## Script (Python) "getNumOfPeriods"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start, end, starthour=0, endhour=24
##title=Get calendar periods (hours or halfhours) from start to event 
##
"""
returns integer number of periods (hours or halfhours) from start of calendar 
  to event.  works for weekbyhour or day view.

mod by lupa, CalendarX-0.6.2, mod to make it more readable.
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
useHalfHours = context.getCXAttribute('useHalfHours')


#cheaper: no DateTime conversions needed, but get the real hours between start and end
if viewstarthour == 0 and viewendhour == 24:
    if useHalfHours:
        periods = int( (end.timeTime() - start.timeTime()) / 1800 )
    else:
        periods = int( (end.timeTime() - start.timeTime()) / 3600 )

#uses DateTime conversion to test inside view periods
else:
    #use bools as heaviside (boxcar) fn
    # i.e., counts if period is viewable, doesn't count if outside view hours range.
    if useHalfHours:
        shalfhour = int(start.timeTime()/60/30)
        ehalfhour = int(end.timeTime()/60/30)
        #use len of a list comprehension to loop through the halfhours, count how many are "in" the view.
        periods = len([1 for halfhr in range(shalfhour,ehalfhour) if viewstarthour <= DateTime(halfhr*30*60).hour() < viewendhour])
    else:
        shour = int(start.timeTime()/60/60)
        ehour = int(end.timeTime()/60/60)
        #use a list comprehension to loop through the hours, count how many are "in" the view.
        periods = len([1 for hr in range(shour,ehour) if viewstarthour <= DateTime(hr*60*60).hour() < viewendhour])
    
return periods
