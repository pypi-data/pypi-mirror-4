from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IColumn
from plone.app.layout.navigation.interfaces import INavigationRoot

class IFooterPortletManager(IPortletManager, IColumn):
    """
    Superclass used by our adapter
    The IColumn bit means that we can add all the portlets available to 
     the right-hand and left-hand column portlet managers
    """

class FooterPortletRenderer(ColumnPortletManagerRenderer):
    """
    A renderer for the content-well portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IFooterPortletManager)
    template = ViewPageTemplateFile('footer_renderer.pt')



from zope.component import getMultiAdapter, ComponentLookupError
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.portlets.interfaces import IPortletManager
from fractions import Fraction

class FooterPortletsViewlet(ViewletBase):

    name = 'FooterPortletManager'
    manage_view = '@@manage-portletsfooter'

    def update(self):
        super(FooterPortletsViewlet, self).update()
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        self.manageUrl =  '%s/%s' % (context_state.view_url(), self.manage_view)

        ## This is the way it's done in plone.app.portlets.manager, so we'll do the same
        mt = getToolByName(self.context, 'portal_membership')
        self.canManagePortlets = mt.checkPermission('Portlets: Manage portlets', self.context)

    def showPortlets(self):
        return '@@manage-portlets' not in self.request.get('URL')

    def portletManagers(self):
        managers = []
        try:
            for n in range(1,7):
                name = 'ContentWellPortlets.%s%s' % (self.name, n)
                mgr = getUtility(IPortletManager, name=name, context=self.context)
                managers.append((mgr,name))
            return managers
        except ComponentLookupError:
            return []

    def portletManagersToShow(self):
        visibleManagers = []
        for mgr, name in self.portletManagers():
            if mgr(self.context, self.request, self).visible:
                visibleManagers.append(name)
        
        managers = []
        numManagers = len(visibleManagers)
        for counter, name in enumerate(visibleManagers):
            pos = 'position-%s' % str(Fraction(counter, numManagers)).replace('/',':')
            width = 'width-%s' % (str(Fraction(1, numManagers)).replace('/',':') if numManagers >1 else 'full')
            managers.append((name, 'cell %s %s %s' % (name.split('.')[-1], width, pos)))
        return managers


from plone.app.portlets.browser.manage import ManageContextualPortlets


class FooterManagePortlets(ManageContextualPortlets):

    def check_navigation_root(self):
        if not INavigationRoot.providedBy(self.context):
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u"plone_portal_state")
            root_url = portal_state.navigation_root_url()
            url = '%s/@@manage-portletsfooter' % root_url
            self.request.response.redirect(url)
            return False

        return True
