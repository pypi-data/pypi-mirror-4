## Script (Python) "sl_ui_variables.js"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=a='',b=''
##title=
##
#add global simpelayout ui variables here...

#init simplelayout object
print """
var simplelayout = new Object();
"""

align_to_grid = 0
grid = getattr(context.aq_inner.aq_explicit, 'align_to_grid', '0')
if int(grid):
    align_to_grid = 1

print """
simplelayout.align_to_grid = %s
""" % (align_to_grid)

return printed
