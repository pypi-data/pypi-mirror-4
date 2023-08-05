from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets import ViewletBase


class CookiePolicyViewlet(ViewletBase):

    enabled = False
    title = ""
    message = ""

    render = ViewPageTemplateFile("templates/cookiepolicy.pt")

    def __init__(self, context, request, view, manager):
        super(CookiePolicyViewlet, self).__init__(context, request, view,
                                                  manager)
        pp = getToolByName(context, 'portal_properties')

        self.sheet = getattr(pp, 'tlspu_cookiepolicy_properties', None)
        if self.sheet:
            self.enabled = self.sheet.getProperty("TCP_enabled", True)
            self.title = self.sheet.getProperty("TCP_title", "Cookie Warning")
            self.message = self.sheet.getProperty(
                "TCP_message",
                "This site uses cookies but the owner has not explained why!")

    def update(self):
        return
