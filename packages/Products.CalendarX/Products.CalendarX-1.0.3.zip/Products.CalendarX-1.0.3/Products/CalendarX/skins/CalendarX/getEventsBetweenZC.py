## Script (Python) "getEventsBetweenZC"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start, end, xmy, xsub, xpub, xcrt
##title=Get Events between dates, using ZCatalog query dictionary
##
"""
Queries the catalog for Events between two dates using the ZCatalog query.

modified for CalendarX 0.9.6(stable) for listOfSubjects bug
Released under the GPL (see LICENSE.txt)
does NOT use AdvancedQuery product of Dieter
 List of variables used
 xmy = improved MY/PUBLIC event switcher: MY == any review_state + user == CREATOR
 xsub = category to view (from Subject -- works with existing CMFEvents and ATEvents)
 xpub = default 1 query for published, 0 = not queried for published status, 'visible' for visible status
 xcrt = (creator) default 1 for no test (view events from anyone), or 0 = query for user = CREATOR,
 xgroups = show shared private events to shared (listed) group members.
"""
#initialize a query dictionary that we will send to the catalog
qdict = {}

#START and END datetime objects (not date strings)
qdict['start'] = dict(query=[start,end], range="min:max")
qdict['sort_on'] = 'start'


#RESTRICTS query to certain portal types, if option is checked in calendar_properties
if context.getCXAttribute('restrictToThisListOfTypes'):
    qdict['portal_type'] = context.getCXAttribute('eventTypes')

#RESTRICTS query to certain paths, if paths are listed in calendar_properties
#make sure paths listed are fully comparable to the paths as listed in the path index
if context.getCXAttribute('restrictToThisListOfPaths'):
    qdict['path'] = context.getCXAttribute('listOfPaths')

#RESTRICTS query to the same path as the CalendarX instance
if context.getCXAttribute('restrictToThisFolder'):
    qdict['path'] = '/'.join(context.getPhysicalPath()[:-1])


#XMY: build an xmy query for MY/PUBLIC requests
#  if 'xmy' == '0', then we don't need xmy in the query
#  (mod 0.4.11)
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
if xpub == '0':
    q_xpub = []
elif xpub == 'visible':
    q_xpub = ['visible']
else:
    q_xpub = ['published']
if context.getCXAttribute('includeReviewStateVisible'):
    q_xpub = ['visible','published']
if xpub == 'pend':
    q_xpub.append('pending')
showForGroups = context.getCXAttribute('showPrivateEventsToGroupMembers')
if showForGroups:
    q_xpub.append('private')
extraStates = context.getCXAttribute('listOfReviewStatesDisplayed')
for state in extraStates:
    q_xpub.append(state)
if xpub  == '11':   #override other requests for Personal Events calendar call
    q_xpub = []



#XCRT CREATOR
#  if 'xcrt' (Creator) == '11', then we want to show ONLY those events
#  in the query for which this user is Creator
xcrt = str(xcrt)
if xcrt == '11':
    q_xcrt = context.portal_membership.getAuthenticatedMember().getUserName()
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
#  (mod 0.6.6) initialize q_xsub as empty list instead of zero.
#  (mod 0.9.6) fixed bug where ALL was not restricted properly to listOfSubjects
q_xsub = []
xsub = str(xsub)
xsub = string.split(xsub, ",")
# if ALL is not in xsub, then we use xsub for the query
if 'ALL' not in xsub:
    q_xsub = xsub
# if ALL is alone in xsub, then we don't need the query at all (q_xsub remains 0)
if 'ALL' in xsub:
    if len(xsub) > 1:
        xsub.remove('ALL')
        q_xsub = xsub
#add this if clause to filter for restricted Subject list
if context.getCXAttribute('restrictToThisListOfSubjects'):
    if 'ALL' in xsub:
        filterlist = context.getCXAttribute('listOfSubjects')
        q_xsub = [sub for sub in filterlist]
    else:
        filterlist = context.getCXAttribute('listOfSubjects')
        q_xsub = [sub for sub in q_xsub if sub in filterlist]



#BUILD QUERY
"""
Build the qdict query dictionary for ZCatalog based on the tests above
No query is needed for xmy: it just sets xcrt and xpub appropriately
"""
if q_xpub is not []:
    qdict['review_state'] = q_xpub
if q_xcrt:
    qdict['Creator'] = q_xcrt
if q_xsub:
    qdict['Subject'] = q_xsub

return context.portal_catalog(qdict)
