# -*- coding: utf-8 -*-

"""Configlets using zope.formlib
"""

from zope.formlib import form
from zope.app.form.browser import MultiCheckBoxWidget as MultiCheckBoxWidget_

from plone.app.controlpanel.form import ControlPanelForm
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from xhostplus.social.interfaces.configuration import ISocialConfiguration
from xhostplus.social import socialMessageFactory as _

class SocialConfiguration(ControlPanelForm):
    form_fields = form.Fields(ISocialConfiguration)

    base_template = ControlPanelForm.template
    template = ViewPageTemplateFile('social_configuration.pt')

    label = _(u"Social Network Configuration")
    description = _(u'Please enter the configuration.')
    form_name = _("Privacy settings")
