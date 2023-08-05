from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost


def setupVarious(context):
    if not context.readDataFile('mockmailhost_various.txt'):
        return
    site = context.getSite()
    replace_mailhost(site)


def replace_mailhost(self):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    portal._delObject('MailHost')
    portal._setObject('MailHost', portal.MockMailHost)

    sm = self.getSiteManager()
    sm.registerUtility(portal.MailHost, provided=IMailHost)
