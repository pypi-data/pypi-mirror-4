## Script (Python) "queriesUnique"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=query
##title=Returns a uniqued catalog brain from a non-unique query brain 
##
"""
returns Brain of unique events from a Brain of events not unique

added by lupa, CalendarX 0.2.7
code snippet from CMFCalendar/CalendarTool.py
Released under the GPL (see LICENSE.txt)
query = results from a catalog query.  should be a list.
"""
# Unique the results
results = []
rids = []
for item in query:
    rid = item.getRID()
    if not rid in rids:
        results.append(item)
        rids.append(rid)


"""  SORT FUNCTION NOT USED HERE
def sort_function(x,y):
    z = cmp(x.start,y.start)
    if not z: 
        return cmp(x.end,y.end)
    return z

# Sort by start date
results.sort(sort_function)
"""

return results
