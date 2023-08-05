## Script (Python) "listUnique"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=list=[],listOfSubjects=0
##title=Returns a uniqued list from a non-unique list
##
"""
returns list of unique values from a list of values not unique
  and if listOfSubjects is True, creates a unique list of subjects from that attribute

modified for CalendarX 0.4.0(dev) to use context instead of skinobj
Released under the GPL (see LICENSE.txt)
"""

if listOfSubjects:
    losstr = ''
    losraw = context.getCXAttribute('listOfSubjects')
    for sub in losraw:
        losstr = losstr + ',' + sub   #build a string from raw listOfSubjects entries
    los = losstr.split(',')
    list = [sub for sub in los if sub != '']  #gets rid of empty strings

# Unique the results
results = []
vals = []
for item in list:
    val = item
    if not val in vals:
        results.append(item)
        vals.append(item)

return results

