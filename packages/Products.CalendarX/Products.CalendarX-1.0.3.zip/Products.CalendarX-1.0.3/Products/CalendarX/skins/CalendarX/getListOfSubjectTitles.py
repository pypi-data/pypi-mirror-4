## Script (Python) "getListOfSubjectTitles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get listOfSubjectTitles from property sheet, safely
##
"""
returns a list of SubjectTitles that matches the length of the list of 
  subjects in listOfSubjects.

new for CalendarX 0.4.14(stable) to prevent "IndexError: tuple index out of 
  range" that occurs when listOfSubjects is longer than listOfSubjectTitles.
Released under the GPL (see LICENSE.txt)
"""
subjects = []
subjecttitles = []
subjects = context.getCXAttribute('listOfSubjects')
subjecttitles = context.getCXAttribute('listOfSubjectTitles')
stlist = [s for s in subjecttitles]  #must be a list to append 

diff = len(subjects) - len(subjecttitles)
while diff > 0:
    stlist.append('')
    diff -= 1  
return stlist

