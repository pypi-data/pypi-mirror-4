## Script (Python) "getMonthName"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=monthnum=0,list=0
##title=Returns a month name or list of months
##
"""
Returns a month name given a month integer, or a month list

new for CalendarX 0.5.0, backported to 0.4.12 
Released under the GPL (see LICENSE.txt)
"""
    
dayseed = DateTime('2004-01-15')
m = ''
if monthnum:
    m = (dayseed+30*(monthnum-1)).aMonth()
if list:
    m = []
    for mon in range(0,12):
        m.append((dayseed+30*mon).aMonth())
return m

