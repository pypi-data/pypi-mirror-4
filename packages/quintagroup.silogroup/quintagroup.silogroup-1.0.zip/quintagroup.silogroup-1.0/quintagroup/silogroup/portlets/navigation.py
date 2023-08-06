from plone.app.portlets.portlets.navigation import Renderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NavRenderer(Renderer):
    recurse = ViewPageTemplateFile('navigation_recurse.pt')
