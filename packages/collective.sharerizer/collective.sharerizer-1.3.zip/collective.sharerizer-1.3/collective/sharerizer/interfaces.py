from plone.theme.interfaces import IDefaultPloneLayer


class ISharerizerBrowserLayer(IDefaultPloneLayer):
    """Marker applied to the request during traversal of sites that
       have collective.sharerizer installed
    """
