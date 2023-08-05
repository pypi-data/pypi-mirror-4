## Script (Python) "queriesSubtract"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=q1, q2
##title=Returns a brain that subtracts events in q2 from q1.
##
"""
subtracts q2 from q1: looks for objects in q1 that are NOT in q2 and 
  builds a q1new list of those objects, and returns q1new

added by lupa, CalendarX 0.2.7 
Released under the GPL (see LICENSE.txt)
"""

#make a list of RIDs in q2, using a list comprehension:
q2rids = [item.getRID() for item in q2]

#make a new q1 that contains only items with RIDs NOT in q2rids
q1new = [item for item in q1 if not item.getRID() in q2rids]

return q1new



"""
#old way, worked, but before I learned list comprehensions...
#make a list of RIDs in q2
q2rids = []
for item in q2:
    q2rids.append(item.getRID())

#make a new q1 that contains only items with RIDs NOT in q2rids
q1new = []
for item in q1:
    rid = item.getRID()
    if not rid in q2rids:
        q1new.append(item)

return q1new
"""
