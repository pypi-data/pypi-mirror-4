## Controller Python Script "ploneboard_comments_get_conversation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object_=None
##title=Return the conversation for context, if none exists return None
##

if not object_:
    object_ = context

pcc = getattr(context, 'ploneboard_comments_', None)
if pcc is None:
    return None
else:
    conversation =  pcc.get_conversation(object_.UID())
    return conversation
