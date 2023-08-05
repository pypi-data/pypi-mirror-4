# -*- coding: utf-8 -*-
#
# File: NewsPage.py
#
# Copyright (c) 2008 by 
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.PloneboardComments import MessageFactory as _


from Products.PloneboardComments.config import *
from Products.CMFCore.utils import getToolByName

from DateTime import DateTime

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((
    ReferenceField('message_board',
                   relationship = 'relatesTo',
                   multiValued = False,
                   vocabulary='get_available_ploneboards',
                   default=None,
                   widget=ReferenceWidget(label='Message board', description='Select Message board', description_msgid='label_message_boards', i18n_domain="PloneboardComments"),
                   ),
    ReferenceField('forum',
                   relationship = 'KnowsAbout',
                   multiValued = False,
                   vocabulary='get_available_forums',
                   default=None,
                   widget=ReferenceWidget(label='Forum', description='Forum (select and save message board options)', description_msgid='label_forums', i18n_domain="PloneboardComments"),
                   ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

from Products.ATContentTypes.content.folder import ATBTreeFolder

PloneboardComments_schema = ATBTreeFolder.schema.copy() + \
    schema.copy()

from Products.Archetypes.utils import DisplayList
from persistent.dict import PersistentDict
import cgi

from AccessControl import getSecurityManager

##code-section after-schema #fill in your manual code here
##/code-section after-schema

i18n_comments_about = _(u'Kommentarer om')
i18n_comments_prefix = _(u'Kommentarer')
i18n_discussing = _('Diskuterer')

class PloneboardComments(ATBTreeFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPloneboardComments)

    archetype = portal_type = meta_type = 'PloneboardComments'
    _at_rename_after_creation = False

    schema = PloneboardComments_schema

    ##code-section class-header #fill in your manual code here
    exclude_from_nav = True
    ##/code-section class-header

    # Methods

    def setId(self, *a, **kw):
        # Always set default ID
        if self.id != 'ploneboard_comments_':
            super(PloneboardComments, self).setId('ploneboard_comments_')

    def get_available_ploneboards(self):
        """Returns a DisplayList of available Ploneboard instances."""
        # Portal catalog sorts out if there is a view permission
        displaylist = DisplayList()
        for board in self.portal_catalog(meta_type='Ploneboard'):
            board = board.getObject()
            title = ""
            title += board.getParentNode().Title()
            title += " - " + board.Title()
            displaylist.add(board.UID(), title)
        return displaylist

    def get_available_forums(self):
        """Returns a DisplayList of available Ploneboard forums in select Ploneboard."""
        # Portal catalog sorts out if there is a view permission
        ploneboard = self.getMessage_board()
        displaylist = DisplayList()
        if ploneboard is None:
            return displaylist
        else:
            for forum in ploneboard.objectValues('PloneboardForum'):
                displaylist.add(forum.UID(), forum.Title())
        return displaylist

    def get_forum(self):
        """Returns the configured forum."""
        return self.getForum()

    def get_conversation(self, UID):
        """Returns conversations about the context object."""
        if not hasattr(self, '_ploneboard_comments_mapping'):
            self._ploneboard_comments_mapping = PersistentDict()
        conversation = self._ploneboard_comments_mapping.get(UID, '')
        if not conversation:
            return None
        else:
            try:
                return self.uid_catalog(UID=conversation)[0].getObject()
            except IndexError:
                # Conversation has been removed
                del self._ploneboard_comments_mapping[UID]
                return None

    security.declarePublic('create_conversation')
    def create_conversation(self, UID):
        """Creates a conversation on the given UID in the forum.

        If there is already a conversation, don't stop
        but just continue to the conversation."""
        i18n_comments_about_ = self.translate(i18n_comments_about)
        i18n_comments_prefix_ = self.translate(i18n_comments_prefix)
        i18n_discussing_ = self.translate(i18n_discussing)

        REQUEST = self.REQUEST
        RESPONSE = REQUEST.RESPONSE
        discussable = self.uid_catalog(UID=UID)[0].getObject()
        # Check whether the user has access to discuss the
        # object (UID) we're going to create a Conversation on.
        if not getSecurityManager().checkPermission('Reply to item', discussable):
            # Does statusmessages work?
            self.plone_utils.addPortalMessage(self.translate('Sorry, no access to discuss this item', domain='PloneboardComments'))
            #RESPONSE.cookies['statusmessages'] = 
            RESPONSE.redirect(REQUEST['HTTP_REFERER'])            
        if not hasattr(self, '_ploneboard_comments_mapping'):
            self._ploneboard_comments_mapping = PersistentDict()        
        forum = self.get_forum()
        if forum is None:
            self.plone_utils.addPortalMessage(self.translate('No forum configured, contact site admin', domain='PloneboardComments'))
            RESPONSE.redirect(REQUEST['HTTP_REFERER'])
        else:
            conversation = self._ploneboard_comments_mapping.get(UID, '')
            if conversation:
                try:
                    conversation = self.uid_catalog(UID=conversation)[0].getObject()
                except IndexError:
                    # Comment deleted, remove UID
                    del self._ploneboard_comments_mapping[UID]
                    conversation = ''
            if not conversation:
                conversation = forum.addConversation(u'%s %s ' % (i18n_comments_about_.decode('utf-8'), discussable.Title().decode('utf-8')))
                conversation.addComment(i18n_comments_prefix_, 
                   u'%s <a href="./resolveuid/%s">%s</a>' % (i18n_discussing_.decode('utf-8'), discussable.UID(), cgi.escape(discussable.Title().decode('utf-8'))))
                self._ploneboard_comments_mapping[UID] = conversation.UID()
            RESPONSE.redirect(conversation.absolute_url())

registerType(PloneboardComments, PROJECTNAME)
# end of class PloneboardComments

##code-section module-footer #fill in your manual code here
##/code-section module-footer
