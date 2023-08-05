## Script (Python) "getAddNewEventURL.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=return URL for Add New Event link
##
##
"""
Returns a URL for the Add New Event link based on property sheet values

mod by lupa for CalendarX-0.6.5 to fix bug when Manager is not a site Member, but the
  AddNewEvent link is set to go to the Member Folder
Released under the GPL (see LICENSE.txt)
"""

ANEUrl = ''
if context.getCXAttribute('useMemberFolder'):
    ANEUrl = container.portal_membership.getHomeUrl()
    if not ANEUrl:
        #falls back to portal root here 
        ANEUrl = container.absolute_url()  
if context.getCXAttribute('useMemberSubfolder'):
    ANEUrl = container.portal_membership.getHomeUrl()
    if not ANEUrl:
        #falls back to portal root here 
        ANEUrl = container.absolute_url()  
    ANEUrl = ANEUrl + context.getCXAttribute('memberSubfolderPath')
if context.getCXAttribute('useANEFolder'):
    ANEUrl = container.absolute_url()+context.getCXAttribute('ANEFolderPath')
if context.getCXAttribute('useUsersAndFolders'):
    userName = container.portal_membership.getAuthenticatedMember().getUserName()
    try:
        userPath = [line.split('|')[1] for line in context.getCXAttribute('listOfUsersAndFolders') if line.split('|')[0] == userName][0]
        ANEUrl = container.absolute_url()+userPath
    except:
        pass
if context.getCXAttribute('useRolesAndFolders'):
    userRoles = container.portal_membership.getAuthenticatedMember().getRoles()
    try:
        userPath = [line.split('|')[1] for line in context.getCXAttribute('listOfRolesAndFolders') if line.split('|')[0] in userRoles][0]
        ANEUrl = container.absolute_url()+userPath
    except:
        pass


if context.getCXAttribute('useCreateObjectOnClick'):
    ANEUrl = ANEUrl+'/'+context.getCXAttribute('createObjectOnClickCommand')
return ANEUrl
