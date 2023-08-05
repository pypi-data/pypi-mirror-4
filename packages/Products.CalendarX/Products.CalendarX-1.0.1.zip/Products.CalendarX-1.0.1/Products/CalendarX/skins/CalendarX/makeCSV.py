## Script (Python) "makeCSV"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=csvstring
##title=Joins the list of filter parameters into a CSV string
##
"""
returns a CSV (comma separated variables) string from a list.

added by lupa, CalendarX 0.2.9 for use with useMultiSubjects
Released under the GPL (see LICENSE.txt)
code contributed by Scott Sturgeon, openroad.ca
"""
if csvstring.count(csvstring) == 0:
    csvstring = str(','.join(csvstring))
else:
    csvstring = str(csvstring)

return csvstring
