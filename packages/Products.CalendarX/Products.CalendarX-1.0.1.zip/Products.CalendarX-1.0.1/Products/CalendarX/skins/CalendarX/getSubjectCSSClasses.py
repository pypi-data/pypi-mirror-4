## Script (Python) "getSubjectCSSClasses"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=event=None,subject=None,fbc='eventPublished'
##title=return a CSS class name based on the event Subject 
##
"""
return a CSS class name based on the event Subject
  
mod by lupa for CalendarX 0.4.3(dev) to fix unbound classy error in
  0.4.2, and to return a class based on a single subject (as well as event.Subject)
Released under the GPL (see LICENSE.txt)

fbc (fallbackclass): use this to define the CSS class used 
  if no Subject match is found. default is "eventPublished"
for event: returns the first valid CSS class found.  because there may  
  be a list of multiple Subjects, this script goes through the list to 
  find a valid CSS class before giving up and returning the default. 
for subject: returns first corresponding CSS class found, or the default. 
"""

classdict = {}
if context.getCXAttribute('useSubjectCSSClasses'):
    for line in context.getCXAttribute('listOfSubjectCSSClasses'):
        subjname = line.split('|')[0]
        classname = line.split('|')[1]
        classdict[subjname] = classname


if subject:
    subs = [subject]
else:
    subs = event.Subject

classy = 0
for sub in subs:
    if classdict.has_key(sub):
        classy = classdict[sub]
        break
    else:
        classy = 0
if classy:
    return classy
else:
    return fbc

