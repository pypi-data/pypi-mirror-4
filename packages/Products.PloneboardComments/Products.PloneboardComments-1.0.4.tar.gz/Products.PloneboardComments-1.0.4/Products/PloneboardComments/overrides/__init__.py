from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from quills.app.browser.macros import WeblogEntryMacros

WeblogEntryMacros.template = ViewPageTemplateFile('quills_entry_macros.pt')
