## Script (Python) "getCXMacro"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name
##title=name = name of the macro
##
"""
Returns a path to the macros from within the CalendarX default skin property sheets.

modified for CalendarX 0.4.0(dev) to use context instead of skinobj
Released under the GPL (see LICENSE.txt)
name = name of the macro desired.  REQUIRED.
name = macro name to be found in a CalendarX macro sheet
"""
pathy = 'nope'
macroName = name
macrosheetlist = getattr(context,'skinMacros','no such sheet list found')
for sheet in macrosheetlist:
    macrosheet = getattr(context,sheet,'no such macro sheet found')
    try: 
        pathy = macrosheet.macros[macroName]
        break #break after finding a successful match
    except:
        pass
if pathy != 'nope':
    return pathy

return context.CX_props_macros.macros[macroName]  #guess the default value
