import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('collective.sharerizer')


def add_settings(context):
    """Add settings to our property sheet.

    We could create an upgrade profile with a propertiestool.xml and
    an accompanying upgrade step, but to me that feels like overkill.
    Some plain python is fine.
    """
    portal_props = getToolByName(context, 'portal_properties')
    props = portal_props.sharerizer
    wanted = [
        # (propname, proptype, default)
        ('restrict', 'boolean', False),
        ('allowed_types', 'lines', []),
        ]
    for propname, proptype, default in wanted:
        if not props.hasProperty(propname):
            props._setProperty(propname, default, proptype)
            logger.info('sharerizer: added %s property %r with default '
                        'value %r', proptype, propname, default)
