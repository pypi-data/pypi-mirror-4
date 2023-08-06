# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from rt.simpleslider import MessageFactory as _
from rt.simpleslider.interfaces import ISliderSettings


class SliderSettingsEditForm(controlpanel.RegistryEditForm):

    schema = ISliderSettings
    label = _(u"Simple Slider settings")
    description = u""

    def updateFields(self):
        super(SliderSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(SliderSettingsEditForm, self).updateWidgets()


class SliderSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SliderSettingsEditForm
