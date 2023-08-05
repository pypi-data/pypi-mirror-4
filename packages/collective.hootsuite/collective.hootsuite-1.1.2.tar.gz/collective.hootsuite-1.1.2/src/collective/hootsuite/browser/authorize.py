from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getMultiAdapter

from collective.hootsuite.interfaces import IHootsuiteRegistry
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Products.statusmessages.interfaces import IStatusMessage

import json, base64, urllib, urllib2, datetime


class Authorize(BrowserView):
    """ Authorize the site on the hootsuite API
    """

    def __call__(self):
        """ redirect to : http://hootsuite.com/oauth2/authorize?response_type=code&client_id=abc123
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IHootsuiteRegistry)

        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')

        redirect_uri = portal_state.portal_url() + '/@@hootsuite-authorize-step2'

        auth_url = settings.url + '?response_type=code&client_id=' + settings.client_id + '&redirect_uri=' + redirect_uri
        self.context.REQUEST.RESPONSE.redirect(auth_url)


class SecondAuthorizeStep(BrowserView):
    """ Second step on oauth2 hootsuite API
    """

    def __call__(self):
        """ curl -X POST -u 'CLIENT_ID:SECRET_KEY' -d 'grant_type=authorization_code&code=AUTH_CODE' https://hootsuite.com/oauth2/token
        """


        code = self.request.get('code')

        # Get the code or error/error_description parameter
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IHootsuiteRegistry)

        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')

        redirect_uri = portal_state.portal_url() + '/@@hootsuite-authorize-step2'

        url = settings.urltoken
        key_json = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri}
        key_json = urllib.urlencode(key_json)

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, settings.client_id, settings.secret_key)
        urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

        req = urllib2.Request(url, key_json)

        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            contents = error.read()
            resultat = json.loads(contents)
            IStatusMessage(self.request).addStatusMessage(resultat['error'],
                                                      "info")
            self.context.REQUEST.RESPONSE.redirect('@@hootsuite-settings')
            return

        resultat_json = response.read()
        resultat = json.loads(resultat_json)

        settings.token = resultat['access_token']
        expires = datetime.datetime.fromtimestamp(resultat['expires_in'])
        settings.expires = unicode(expires.strftime("%d/%m/%Y %H:%M:%S"))

        self.context.REQUEST.RESPONSE.redirect('@@hootsuite-settings')


class RefreshServices(BrowserView):
    """ Actualize Services List
    """

    def __call__(self):
        """ curl -X POST -u 'CLIENT_ID:SECRET_KEY' -d 'grant_type=authorization_code&code=AUTH_CODE' https://hootsuite.com/oauth2/token
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IHootsuiteRegistry)

        # We need to know the services where to send
        authorization_header = "Bearer %s" % settings.token

        #opener = urllib2.build_opener()
        #opener.addheaders = [('Authorization', authorization_header)]
        #urllib2.install_opener(opener)

        req = urllib2.Request(settings.urlapi + 'networks')
        req.add_header("Authorization", authorization_header)

        try:
            response = urllib2.urlopen(req)
            resultat_json = response.read()
            resultat = json.loads(resultat_json)
        except urllib2.HTTPError, error:
            contents = error.read()
            resultat = json.loads(contents)
            IStatusMessage(self.request).addStatusMessage(resultat['error'],
                                                      "info")
            self.context.REQUEST.RESPONSE.redirect('@@hootsuite-settings')
            return

        services = []
        for res in resultat['results']:
            services.append(res['username']+" "+res['type']+" "+str(res['socialNetworkId']))

        settings.possible_services = services
        self.context.REQUEST.RESPONSE.redirect('@@hootsuite-settings')
