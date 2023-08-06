from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase


class SiteFullscreenViewlet(ViewletBase):
    render = ViewPageTemplateFile('toggle_sitefullscreen.pt')

