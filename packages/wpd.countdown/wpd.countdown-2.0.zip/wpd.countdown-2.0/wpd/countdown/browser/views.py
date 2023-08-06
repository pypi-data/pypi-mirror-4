# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from Products.CMFPlone import PloneMessageFactory as _
from zope.interface import Interface
from zope.schema import Date, URI


class IWPDSchema(Interface):

    wpd_date = Date(title=_(u'Date of the World Plone Day'),
                    required=True)

    wpd_url = URI(title=_(u'URL to a local WPD Website'),
                  required=False)


class WPDSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IWPDSchema
    label = _(u"World Plone Day settings")
    description = _(u"""""")

    def updateFields(self):
        super(WPDSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(WPDSettingsEditForm, self).updateWidgets()


class WPDSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = WPDSettingsEditForm
