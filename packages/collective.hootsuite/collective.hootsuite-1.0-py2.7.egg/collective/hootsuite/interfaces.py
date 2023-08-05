from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.hootsuite')


class IHootsuiteRegistry(Interface):
    """ Interface for plone registry configuration
    """

    token = schema.TextLine(title=u"Token",
            description=u"",
            required=False)

    possible_services = schema.List(title=u"Services available",
                               description=u"",
                               required=False,
                               readonly=True,
                               default=[],
                               )

    active_services = schema.List(title=u"Services enabled",
                               description=u"",
                               required=False,
                               value_type=schema.Choice(vocabulary=u"collective.hootsuite.ids"),
                               )

    client_id = schema.TextLine(title=u"Client ID",
                description=u"")

    secret_key = schema.TextLine(title=u"Secret Key",
                 description=u"")

    portal_types = schema.List(title=u"Portal types enabled",
                               description=u"",
                               required=False,
                               value_type=schema.Choice(vocabulary=u"plone.app.vocabularies.PortalTypes"),
                               )

    url = schema.TextLine(title=u"URL to authorize",
            description=u"URL to access authorization",
            default=u"http://hootsuite.com/oauth2/authorize",
            readonly=True)

    urltoken = schema.TextLine(title=u"URL to get token",
            description=u"URL to access token",
            default=u"https://hootsuite.com/oauth2/token",
            readonly=True)

    urlapi = schema.TextLine(title=u"URL to get API",
            description=u"URL to get API",
            default=u"https://api.hootsuite.com/api/2/",
            readonly=True)

    expires = schema.TextLine(title=u"When it expires",
            description=u"When the Hootsuite token expires",
            required=False)
