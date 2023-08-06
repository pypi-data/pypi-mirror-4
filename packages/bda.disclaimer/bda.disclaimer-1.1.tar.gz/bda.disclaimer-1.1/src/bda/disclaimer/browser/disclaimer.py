from zExceptions import Redirect
from zope.component import ComponentLookupError
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five import BrowserView
from Products.CMFPlone.utils import getToolByName
from bda.disclaimer.interfaces import IDisclaimerText


class DisclaimerViewlet(ViewletBase):

    def update(self):
        self.accepted = self.request.cookies.get('_dc_acc')

    def render(self):
        if self.accepted \
          or self.request['ACTUAL_URL'].endswith('/@@disclaimer'):
            return ''
        purl = getToolByName(self.context, 'portal_url')
        pobj = purl.getPortalObject()
        url = '%s/%s' % (pobj.absolute_url(), '@@disclaimer')
        raise Redirect(url)


class DisclaimerPage(BrowserView):

    def currentlang(self):
        plt = getToolByName(self.context, 'portal_languages')
        if not plt:
            return None
        return plt.getLanguageBindings()[0]

    def pagetitle(self):
        purl = getToolByName(self.context, 'portal_url')
        pobj = purl.getPortalObject()
        return pobj.title

    def checkdisclaimer(self):
        display = True
        if self.request.form.get('_dc_accept') == '1' \
          and self.request.form.get('_dc_submitted'):
            self.request.response.setCookie('_dc_acc', '1', path='/')
            display = False
        elif self.request.cookies.get('_dc_acc'):
            display = False
        if not display:
            purl = getToolByName(self.context, 'portal_url')
            pobj = purl.getPortalObject()
            url = pobj.absolute_url()
            raise Redirect(url)

    def disclaimertext(self):
        try:
            return IDisclaimerText(self.context)()
        except ComponentLookupError, e:
            return 'No Disclaimer text registered. %s' % str(e)
        except AttributeError, e:
            return 'Disclaimer Text not provided properly. %s' % str(e)
