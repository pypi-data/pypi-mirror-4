# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.i18nmessageid import MessageFactory
from plone.fieldsets.fieldsets import FormFieldsets
from plone.app.controlpanel.form import ControlPanelForm

from jalon.primo import contentMessageFactory as _
from jalon.primo.interfaces.utility import IPrimoLayout
from jalon.primo.browser.interfaces.controlpanel import IPrimoControlPanelForm

class PrimoControlPanelForm(ControlPanelForm):
    """Primo Control Panel Form"""
    implements(IPrimoControlPanelForm)

    primolayout = FormFieldsets(IPrimoLayout)
    primolayout.id = 'primolayout'
    primolayout.label = _(u'Connexion')

    form_fields = FormFieldsets(primolayout) # Primolibraries

    label = _(u"Primo Settings")
    description = _(u"Settings for the Primo connector.")
    form_name = _("Primo Settings")
