# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from jalon.apogee import contentMessageFactory as _


class IApogeeLayout(Interface):
    """This interface defines the layout properties."""

    url_connexion = schema.TextLine(
        title=_(u"Url de connexion à la base Apogée."),
        description=_(u"exemple : dbschema://username:password@hostname/databasename"),
        required=True)

    cod_anu = schema.TextLine(
        title=_(u"Année universitaire courante"),
        description=_(u"exemple : 2010"),
        required=True)

    uel = schema.TextLine(
        title=_(u"Valeur de base de la liste des UEL"),
        description=_(u"exemple : WUEL0"),
        required=True)

    type_base = schema.TextLine(
        title=_(u"Type de la connexion base de données utilisée"),
        description=_(u"exemple : apogee"),
        required=True)


class IApogee(
    IApogeeLayout,
    ):
    """This interface defines the Utility."""

    def getContentType(self, object=None, fieldname=None):
        """Get the content type of the field."""

    def getConfiguration(self, context=None, field=None, request=None):
        """Get the configuration based on the control panel settings and the field settings.
        request can be provide for translation purpose."""
