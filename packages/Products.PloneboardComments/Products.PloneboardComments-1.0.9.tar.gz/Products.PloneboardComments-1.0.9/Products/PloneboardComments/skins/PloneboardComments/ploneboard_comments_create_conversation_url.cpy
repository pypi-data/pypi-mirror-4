## Controller Python Script "ploneboard_comments_create_conversation_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object=None
##title=Return the conversation for context, if none exists return None
##

if not object:
    object = context

pcc = getattr(context, 'ploneboard_comments_')
if pcc is not None:
    UID = object.UID
    if callable(UID):
        UID = UID()
    url = pcc.absolute_url() + '/create_conversation?UID=' + UID
    return url
else:
    return 'javascript:alert("Failed to generate discussion URL")'
