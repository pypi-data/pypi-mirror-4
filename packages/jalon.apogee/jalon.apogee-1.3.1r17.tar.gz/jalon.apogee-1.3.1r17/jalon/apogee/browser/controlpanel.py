# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.i18nmessageid import MessageFactory
from plone.fieldsets.fieldsets import FormFieldsets
from plone.app.controlpanel.form import ControlPanelForm

from jalon.apogee import contentMessageFactory as _
from jalon.apogee.interfaces.utility import IApogeeLayout
from jalon.apogee.browser.interfaces.controlpanel import IApogeeControlPanelForm

class ApogeeControlPanelForm(ControlPanelForm):
    """Apogee Control Panel Form"""
    implements(IApogeeControlPanelForm)

    apogeelayout = FormFieldsets(IApogeeLayout)
    apogeelayout.id = 'apogeelayout'
    apogeelayout.label = _(u'Connexion')
    form_fields = FormFieldsets(apogeelayout) # Apogeelibraries

    label = _(u"Apogee Settings")
    description = _(u"Settings for the Apogee connector.")
    form_name = _("Apogee Settings")
