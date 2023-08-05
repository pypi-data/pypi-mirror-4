from plone.app.layout.viewlets.content import DocumentActionsViewlet as base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class DocumentActionsViewlet(base):

    index = ViewPageTemplateFile("document_actions.pt")

    def getShareCode(self):
        """Return the javascript/html for sharing"""
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        # The default is to not restrict the portal_types where the
        # code is shown.
        if s_props.restrict:
            if self.context.portal_type not in s_props.allowed_types:
                return ''
        return s_props.code

    def getShareIcon(self):
        """Return the boolean for Document Action Icons"""
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        return s_props.daicon
