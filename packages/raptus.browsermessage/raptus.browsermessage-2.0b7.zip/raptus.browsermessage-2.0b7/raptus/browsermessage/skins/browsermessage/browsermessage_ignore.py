## Script (Python) "browsermessage_ignore"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

context.REQUEST.SESSION.set('browsermessage_ignore', 1)

return 'success'