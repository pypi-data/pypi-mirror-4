import random

from AccessControl import getSecurityManager

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.portlet.collection import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName


class IRecentCommentsPortlet(IPortletDataProvider):
    """A portlet which renders the results of a collection object.
    """


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IRecentCommentsPortlet)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return "Recent comments portlet"

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('recentComments.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return True

    def css_class(self):
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-collection-%s" % normalizer.normalize(header)


class AddForm(base.NullAddForm):
     """Portlet add form.
     """
     def create(self):
         return Assignment()
