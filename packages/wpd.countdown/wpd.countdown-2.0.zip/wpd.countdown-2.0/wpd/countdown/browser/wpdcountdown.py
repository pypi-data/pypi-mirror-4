from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import datetime

from Products.CMFCore.utils import getToolByName

from wpd.countdown import MessageFactory as _
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from wpd.countdown.browser.views import IWPDSchema


class IWPDcountdown(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IWPDcountdown)

    @property
    def title(self):
        """
        """
        return _(u"WPD Countdown")


class AddForm(base.NullAddForm):
    """Portlet add form.
    """
    def create(self):
        return Assignment()


class Renderer(base.Renderer):
    """Portlet renderer.
    """

    def getDate(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWPDSchema)
        wpd_date = settings.wpd_date
        return datetime(wpd_date.year, wpd_date.month, wpd_date.day)

    def days(self):
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        return (self.getDate() - today).days

    def prettyDate(self):
        translation_service = getToolByName(self, 'translation_service')
        return translation_service.ulocalized_time(self.getDate())

    def getUrl(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWPDSchema)
        return settings.wpd_url

    @property
    def isToday(self):
        return self.days() == 0

    @property
    def isPast(self):
        return self.days() < 0

    @property
    def isFuture(self):
        return self.days() > 0

    render = ViewPageTemplateFile('wpdcountdown.pt')
