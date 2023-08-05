"""Common configuration constants
"""

from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'PloneboardComments'

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

ADD_CONTENT_PERMISSIONS = {
    'PloneboardComments': 'PloneboardComments: Add PloneboardComments',
}

setDefaultRoles('PloneboardComments: Add PloneboardComments', ('Manager','Owner'))

ADD_PERMISSIONS = {
    'PloneboardComments': 'PloneboardComments: Add PloneboardComments',
}
