# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from jalon.primo import contentMessageFactory as _

class IPrimoLayout(Interface):
    """This interface defines the layout properties."""

    url_connexion = schema.TextLine(
        title=_(u"Url de la librairie xml-rpc sur serveur ExLibris Primo"),
        description=_(u"exemple : http://domainname.com/api/xml"),
        required=True)

    url_catalogue = schema.TextLine(
        title=_(u"Url du catalogue Primo"),
        description=_(u"exemple : http://BUPrimo.fr"),
        required=True)

    url_acquisition = schema.TextLine(
        title=_(u"Url pour suggerer de nouvelles acquisitions à votre BU"),
        description=_(u"exemple : http://BUPrimo.fr/acquisitions"),
        required=False) 

    login = schema.TextLine(
        title=_(u"Nom d'utilisateur du compte administrateur du serveur ExLibris Primo"),
        description=_(u"exemple : admin"),
        required=True) 
 
    password = schema.Password(
        title=_(u"Mot de passe du compte administrateur ExLibris Primo"),
        description=_(u"exemple : admin"),
        required=True) 

class IPrimo(IPrimoLayout):
    """This interface defines the Utility."""

    def getContentType(self, object=None, fieldname=None):
        """Get the content type of the field."""

    def getConfiguration(self, context=None, field=None, request=None):
        """Get the configuration based on the control panel settings and the field settings.
        request can be provide for translation purpose."""
