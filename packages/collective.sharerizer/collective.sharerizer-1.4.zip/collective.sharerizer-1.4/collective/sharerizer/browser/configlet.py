from zope import schema
from zope.formlib.form import FormFields

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from plone.app.controlpanel.form import ControlPanelForm

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName


class ISharerizerCode(Interface):

    code = schema.Text(
        title=u"Paste code here",
        description=(u"Paste the complete code snippet provided"
                     u" by the service."),
        required=False,
        )

    daicon = schema.Bool(
        title=u"Display Document Actions Icons",
        description=u"Check to display Document Action Icons.",
        required=False,
        )

    restrict = schema.Bool(
        title=u"Restrict types",
        description=u"Restrict the types for which the code is shown.",
        required=False,
        )

    allowed_types = schema.List(
        title=u"Allowed types",
        description=(u"Select the types for which the code is shown, "
                     u"if the restricted setting is used."),
        required=False,
        value_type=schema.Choice(source='plone.app.vocabularies.PortalTypes'),
        )


class SharerizerCPAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(ISharerizerCode)

    def setCode(self, value):
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        s_props.manage_changeProperties(code=value)

    def getCode(self):
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        return s_props.code

    code = property(getCode, setCode)

    def setIcon(self, value):
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        s_props.manage_changeProperties(daicon=value)

    def getIcon(self):
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        return s_props.daicon

    daicon = property(getIcon, setIcon)

    def setRestrict(self, value):
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        s_props.manage_changeProperties(restrict=value)

    def getRestrict(self):
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        return s_props.restrict

    restrict = property(getRestrict, setRestrict)

    def setAllowed_types(self, value):
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        s_props.manage_changeProperties(allowed_types=value)

    def getAllowed_types(self):
        portal_properties = getToolByName(self.context, 'portal_properties')
        s_props = getattr(portal_properties, 'sharerizer')
        return s_props.allowed_types

    allowed_types = property(getAllowed_types, setAllowed_types)


class SharerizerCP(ControlPanelForm):

    form_fields = FormFields(ISharerizerCode)

    # title of the page
    label = u"Sharerizer settings"
    # explanatory text
    description = u"""collective.sharerizer allows you to use sharing services
                      such as ShareThis and AddThis in your Plone site. Paste
                      the code snippet that your service gives you into
                      the input below, and it will be injected into this
                      site's "document actions" (which are the links on each
                      page such as "Email This" and "Print This")."""
    form_name = "Sharerizer settings"
