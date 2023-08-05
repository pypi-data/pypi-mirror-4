## Controller Python Script "ploneboard_comments_get_forum"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return the configured PloneboardComments config in context
##

# Looks for a configured forum, returns None if
# there isn't one.
pcc = getattr(context, 'ploneboard_comments_', None)
if pcc:
    return pcc.getMessage_board()
else:
    return None
