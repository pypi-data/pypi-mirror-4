## Script (Python) "getSubjectCSSClasses"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=event=None,type=None,fbc='eventPublished'
##title=return a CSS class name based on the event Type 
##
"""
return a CSS class name based on the event Type (portal type)
  
added by lupa for CalendarX 0.4.7(alpha) 
Released under the GPL (see LICENSE.txt)

fbc (fallbackclass): use this to define the CSS class used 
  if no Subject match is found. default is "eventPublished"
for event: returns the first valid CSS class found.  because there may  
  be a list of multiple Types, this script goes through the list to 
  find a valid CSS class before giving up and returning the default. 
for type: returns first corresponding CSS class found, or the default. 
"""

classdict = {}
if context.getCXAttribute('useEventTypeCSSClasses'):
    for line in context.getCXAttribute('listOfEventTypeCSSClasses'):
        key = line.split('|')[0]
        classname = line.split('|')[1]
        classdict[key] = classname

classy = 0
if classdict.has_key(type):
    return classdict[type]
else:
    return fbc



