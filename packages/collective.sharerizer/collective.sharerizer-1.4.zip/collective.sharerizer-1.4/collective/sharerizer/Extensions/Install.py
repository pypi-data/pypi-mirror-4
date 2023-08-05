from Products.CMFCore.utils import getToolByName


def uninstall(portal, reinstall=False):
    """If we're not reinstalling remove cruft from portal (portal_properties
    and portal_controlpanel)
    """

    if not reinstall:
        portal_properties = getToolByName(portal, "portal_properties")
        if 'sharerizer' in portal_properties:
            portal_properties._delObject('sharerizer')

        controlpanel = getToolByName(portal, 'portal_controlpanel')
        if 'sharerizer' in [a.getId() for a in controlpanel.listActions()]:
            controlpanel.unregisterConfiglet('sharerizer')
