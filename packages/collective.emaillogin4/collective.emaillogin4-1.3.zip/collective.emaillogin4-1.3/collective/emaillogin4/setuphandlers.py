from Products.CMFCore.utils import getToolByName

from patches.pa_upgrade.final import to424_pas_interfaces
from patches.pa_controlpanel.security import migrate_to_email_login


def setup_various(context):
    """Miscellaneous steps to perform when (re)installing the product."""
    if context.readDataFile('collective.emaillogin4.txt') is None:
        return
    site = context.getSite()
    # If email as login was already switched on, we should lowercase
    # all login names.
    to424_pas_interfaces(site)

    # Switch email login on.  This would NOT be done when merging this
    # package back to core Plone.
    ptool = getToolByName(site, 'portal_properties')
    if not ptool.site_properties.getProperty('use_email_as_login'):
        migrate_to_email_login(site)
