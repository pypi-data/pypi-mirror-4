from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class GlobalSocialViewlet(ViewletBase):
    index = ViewPageTemplateFile('global_social.pt')