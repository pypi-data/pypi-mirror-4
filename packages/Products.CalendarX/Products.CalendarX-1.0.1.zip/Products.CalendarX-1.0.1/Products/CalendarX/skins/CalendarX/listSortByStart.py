## Script (Python) "listSortByStart"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=list=[]
##title=Returns a list of events sorted by start
##
"""
returns list of sorted events from a list of events not sorted

added for CalendarX 0.6.4 because we needed it.
Released under the GPL (see LICENSE.txt)
"""


#SORT FUNCTION USED HERE
def sort_function(x,y):
    z = cmp(x.start,y.start)
    if not z: 
        return cmp(x.end,y.end)
    return z

list.sort(sort_function)
return list

