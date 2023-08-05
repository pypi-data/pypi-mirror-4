## Script (Python) "isCalendarManager"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=boolean returned based on status of current user 
##
"""
returns True (1) if current user is considered a "Calendar Manager"

added for CalendarX 0.4.3(dev) by lupa zurven
Released under the GPL (see LICENSE.txt)
"""
#  CHECKS USER FOR "Manager" ROLE
#  RETURNS TRUE IF USER IS A "Manager"
roles = context.portal_membership.getAuthenticatedMember().getRoles()
isCalMan = "Manager" in roles
if isCalMan:
    return 1
else:
    return 0


"""
#CODE EXAMPLE: ANOTHER APPROACH
#  CHECKS GROUPS FOR MEMBERSHIP IN "CalendarManager" GROUP
#  RETURNS TRUE IF USER IS A MEMBER
#  CODE WORKS, BUT SHOULDN'T USE NAKED TRY:EXCEPT

user = context.portal_membership.getAuthenticatedMember()
try:
    ugroups = user.getGroups()
except:
    ugroups = 0
if ugroups and 'group_CalendarManager' in ugroups:
    return 1
return 0
"""

