## Script (Python) "getCXSheetlist"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=make list of CalendarX property sheet objects in context
##
"""
Makes a list of CalendarX property sheet objects to hold during calendar generation
  and avoid hitting Plone skins mechanism too many times creating a view.  Speeds 
  up the month view by about 300%.

new for CalendarX-0.5.1 to speed things up
Released under the GPL (see LICENSE.txt)
"""
CXsheetlist = []
sheetnamelist = getattr(context,'skinSheets','no such sheet list found')
for sheetname in sheetnamelist:
    CXsheetlist.append(getattr(context,sheetname))
return CXsheetlist


