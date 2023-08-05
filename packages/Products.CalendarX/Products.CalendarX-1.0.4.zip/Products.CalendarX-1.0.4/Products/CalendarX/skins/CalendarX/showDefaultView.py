## Script (Python) "showDefaultView"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=redirects to default calendar view
##
"""
redirects to default calendar view

mod by lupa for CalendarX-0.9.0(dev)
Released under the GPL (see LICENSE.txt)
"""
dest = context.getCXAttribute('defaultView')
return context.REQUEST.RESPONSE.redirect('%s/%s' % (context.absolute_url(), dest))
