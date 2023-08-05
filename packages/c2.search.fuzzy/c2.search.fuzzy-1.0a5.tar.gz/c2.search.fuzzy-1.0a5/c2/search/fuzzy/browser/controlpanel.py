# encoding: utf-8

from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from c2.search.fuzzy import c2SearchFuzzyMassage as _

class IFuzzySearchPanel(ISiteRoot):
    """Contents import by csv.
    """

class FuzzySearchPanel(BrowserView):
    implements(IFuzzySearchPanel)

    template = ViewPageTemplateFile('controlpanel.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.fuzzy_tool = getToolByName(self.context, 'words_for_fuzzy')
        if self.request.form.get('form.submit.rebuild') == '1':
            self._rebuild()
        return self.template()

    def count(self):
        fuzzy_tool = self.fuzzy_tool
        return fuzzy_tool.length()

    def _rebuild(self):
        fuzzy_tool = self.fuzzy_tool
        fuzzy_tool.rebuild()
        self.context.plone_utils.addPortalMessage(_(u'Rebuild done'))
