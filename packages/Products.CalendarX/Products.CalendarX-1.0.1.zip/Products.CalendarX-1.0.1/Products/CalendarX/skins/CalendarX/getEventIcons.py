## Script (Python) "getEventIcons"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=event,subject=0,type=0
##title=Returns an icon object from the skin based on the Subject or Type
##
"""
returns an icon object from the skin based on the Subject or Event Type
mod by lupa for CalendarX 0.6.1 to trap AttributeError for bad icon name, and 
   cause it to return icon = '', thereby showing NO icon instead of error msg 
Released under the GPL (see LICENSE.txt)
NOTE: Event Type takes precedence over Subject if both are selected in options
NOTE: optimize this whole deal someday.  this recreates these dictionaries 
   for each event in a single view.  ain't really right.  it just ain't right.
   and get rid of the try:excepts as a means of control flow.  sheesh.
"""
#create a dictionary of Icons
#specify the subject too
iconsdict = {}
icon = ""
keyname = ""
if context.getCXAttribute('useSubjectIcons') and not context.getCXAttribute('useEventTypeIcons'):
    for line in context.getCXAttribute('listOfSubjectIcons'):
        key = line.split('|')[0]
        iconname = line.split('|')[1]
        iconsdict[key] = iconname
    keyname = subject
elif context.getCXAttribute('useEventTypeIcons'):
    for line in context.getCXAttribute('listOfEventTypeIcons'):
        key = line.split('|')[0]
        iconname = line.split('|')[1]
        iconsdict[key] = iconname
    keyname = type

    
try:
    icon = getattr(context,iconsdict[keyname])
except AttributeError:
    icon = ""    
except KeyError:
    try:
        icon = getattr(context,event.getIcon)
    except AttributeError:
#        SET ICON="event_icon.gif" FOR DEFAULT EVENT ICON IF ICON NOT FOUND
        icon = getattr(context,"event_icon.gif")
# Alternate behaviors...
#        SET ICON="" FOR NO ICON IF ICON NOT FOUND (no icon will show)
#        icon = ""    
#        SET ICON to lookup object's real icon FOR ICON IF ICON NOT FOUND
#        icon = getattr(context,event.getObject().getIcon())

return icon

