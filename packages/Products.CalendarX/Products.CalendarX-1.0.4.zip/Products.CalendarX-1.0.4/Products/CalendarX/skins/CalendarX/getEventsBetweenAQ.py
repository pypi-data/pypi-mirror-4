## Script (Python) "getEventsBetweenAQ"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start, end, xmy, xsub, xpub, xcrt
##title=Get Events between dates, using AdvancedQuery
##
"""
Queries catalog to retrieve events between two dates using AdvancedQuery.

modified for CalendarX 0.9.6(stable) for listOfSubjects, xcrt & xpaths bugs
Released under the GPL (see LICENSE.txt)
 List of variables used
 xmy = improved MY/PUBLIC event switcher: MY == any review_state + user == CREATOR
 xsub = category to view (from Subject -- works with existing CMFEvents and ATEvents)
 xpub = default 1 query for published, 0 = not queried for published status, 'visible' for visible status
 xcrt = (creator) default 1 for no test (view events from anyone), or 0 = query for user = CREATOR,
 xgroups = show shared private events to shared (listed) group members.
"""

from Products.AdvancedQuery import Between, Eq, Generic, In, Le, Ge

#RESTRICTS query to certain portal types, if option is checked in calendar_properties
q_xtypes = 0
if context.getCXAttribute('restrictToThisListOfTypes'):
    q_xtypes = In('portal_type', context.getCXAttribute('eventTypes'))


#RESTRICTS query to certain paths, if paths are listed in calendar_properties
#make sure paths listed are fully comparable to the paths as listed in the path index
q_xpaths = 0
if context.getCXAttribute('restrictToThisListOfPaths'):
    q_xpaths = In('path', context.getCXAttribute('listOfPaths'))

#RESTRICTS query to the same path as the CalendarX instance
if context.getCXAttribute('restrictToThisFolder'):
    q_xpaths = In('path', '/'.join(context.getPhysicalPath()[:-1]))


#XMY: build an xmy query for MY/PUBLIC requests
#  if 'xmy' == '0', then we don't need xmy in the query
#  if 'xmy' == '1' or anything else, then set xcrt = '11' to ONLY show user == CREATOR
#  and then set xpub = '11' to allow viewing ANY review_state events (including PRIVATE)
xmy = str(xmy)
xcrt = '0'
if xmy == '0':
    q_xmy = 0
else:
    xcrt = '11'
    xpub = '11'



#XPUB  Default shows published, unless exactly xpub='0' for no query
#  make sure xpub is a string. then unless xpub is exactly '0', query on published status
#  (added later) if xpub is exactly 'visible', then show only visible
#  (mod 0.2.10) if "includeReviewStateVisible" attribute is checked, then include visible
#    and override the querystring
#  (mod 0.4.3) if xpub = "pend", then include pending events too
#  (mod 0.4.11) show Private if xmy
#  (mod 0.6.0) showForGroups
xpub = str(xpub)
q_xpub = 0
if xpub == '0':
    q_xpub = 0
elif xpub == 'visible':
    qxpublist = ['visible']
else:
    qxpublist = ['published']
if context.getCXAttribute('includeReviewStateVisible'):
    qxpublist = ['visible','published']
if xpub == 'pend':
    qxpublist.append('pending')
showForGroups = context.getCXAttribute('showPrivateEventsToGroupMembers')
if showForGroups:
    qxpublist.append('private')
extraStates = context.getCXAttribute('listOfReviewStatesDisplayed')
for state in extraStates:
    qxpublist.append(state)
q_xpub = In('review_state', qxpublist)
if xpub == '11':   #override other requests for Personal Events calendar call
    q_xpub = []


#XCREATOR works
#  if 'xcrt' (Creator) == '11', then we want to show ONLY those events
#  in the query for which this user is Creator
xcrt = str(xcrt)
if xcrt == '11':
    q_xcrt = Eq('Creator', context.portal_membership.getAuthenticatedMember().getUserName())
else:
    q_xcrt = 0


#XSUB: build an xsub query of Subject categories
#  if 'xsub' (Subject) == 'ALL', then we don't need xsub in the query
#  mod 0.2.8: UNLESS the "restrictToThisListOfSubjects" property is checked
#   then we have to restrict to the "listOfSubjects" list.
#  initialize q_xsub, make sure xsub is a string, then split xsub into a list
#  (mod 0.6.1) make ALL work ONLY if it is the only item in xsub, rather than
#    overriding other subjects.
#  (mod 0.6.1) change restrictToThisListOfSubjects so that it is a filter
#    instead of overriding the chosen subjects (use a list comprehension).
#  (mod 0.9.6) fixed bug where ALL was not restricted properly to listOfSubjects
q_xsub = 0
xsub = str(xsub)
xsub = string.split(xsub, ",")
# if ALL is not in xsub, then we use xsub for the query
if 'ALL' not in xsub:
    q_xsub = 1
# if ALL is alone in xsub, then we don't need the query at all (q_xsub remains 0)
if 'ALL' in xsub:
    if len(xsub) > 1:
        xsub.remove('ALL')
        q_xsub = 1
#add this if clause to filter for restricted Subject list
if context.getCXAttribute('restrictToThisListOfSubjects'):
    q_xsub = 1
    if 'ALL' in xsub:
        filterlist = context.getCXAttribute('listOfSubjects')
        xsub = [sub for sub in filterlist]
    else:
        filterlist = context.getCXAttribute('listOfSubjects')
        xsub = [sub for sub in xsub if sub in filterlist]

#if flag is 1, then set q_xsub for the Adv Query
if q_xsub == 1:
    q_xsub = In('Subject', xsub)





#BUILD QUERY
"""
Build the query for evalAdvancedQuery based on the tests above
No query is needed for xmy: it just sets xcrt and xpub appropriately
  some old tests:
    query = Between('start', start, end) & Generic(generic_qdict)
    this works: query = Between('start', start, end) & Generic('review_state','published')
    this works: query = Between('start', start, end) &~ q_xpub
    query = Between('start', start, end) &~ q_xpub
"""
query = Between('start', start, end)

if q_xtypes:
    query = query & q_xtypes
if q_xpaths:
    query = query & q_xpaths
if q_xpub:
    query = query & q_xpub
if q_xsub:
    query = query & q_xsub
if q_xcrt:
    query = query & q_xcrt



#RETURN QUERY RESULTS
#sort the query by start date
return context.portal_catalog.evalAdvancedQuery(query,(('start','asc'),))
