from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFDefault.DiscussionTool import DiscussionNotAllowed
from plone.app.layout.viewlets.comments import CommentsViewlet as CV
from Products.Ploneboard.content.PloneboardForum import PloneboardForum

from Acquisition import aq_inner

class CommentsViewlet(CV):

    index = ViewPageTemplateFile('comments.pt')

    def update(self):
        super(CommentsViewlet, self).update()
