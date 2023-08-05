from plone.app.portlets.portlets.navigation import Renderer

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner, aq_base, aq_parent
from Products.CMFPlone import utils

class NBFNavRenderer(Renderer):

    _template = ViewPageTemplateFile('templates/navigation.pt')
    recurse = ViewPageTemplateFile('templates/navigation_recurse.pt')
                  
    def root_is_selected(self):
        context = aq_inner(self.context)
        root = self.getNavRoot()
        if (aq_base(root) is aq_base(context) or
            (aq_base(root) is aq_base(aq_parent(aq_inner(context))) and
             utils.isDefaultPage(context, self.request, context))):
            return True
        else:
            return False
                                                        
