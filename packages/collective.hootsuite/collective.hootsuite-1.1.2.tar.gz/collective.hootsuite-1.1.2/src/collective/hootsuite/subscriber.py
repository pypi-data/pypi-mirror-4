from collective.hootsuite.interfaces import IHootsuiteRegistry
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
import datetime, time, urllib2, json, pytz, urllib
from Products.ATContentTypes.utils import DT2dt
import logging

logger = logging.getLogger("collective.hootsuite")


def update_on_modify(obj, event):
    """ We change the workflow. We check if the type is enabled and the state is published
    """
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IHootsuiteRegistry)
    if (obj.portal_type in settings.portal_types) and (event.new_state.id == 'published'):
        # Send the title to hootsuite
        dataDT = obj.getEffectiveDate()
        data = DT2dt(dataDT)
        # We send now !
        services = []
        for socialId in settings.active_services:
            services.append(int(socialId.split(" ")[-1]))
        title = obj.Title() + " " + obj.absolute_url() + " " + settings.hashtag
        if (datetime.datetime.now().replace(tzinfo=pytz.utc) > data.replace(tzinfo=pytz.utc)):
            tosend = {'message': title, 'socialNetworks': services}
        else:
            tosend = {'message': title, 'socialNetworks': services, 'sendLater': 1, 'sendAlert': 1, 'timestamp': time.mktime(data.timetuple())}

        tosend = json.dumps(tosend)
        #tosend = urllib.urlencode(tosend)
        authorization_header = "Bearer %s" % settings.token
        req = urllib2.Request(settings.urlapi + 'messages', tosend)
        req.add_header("Authorization", authorization_header)

        try:
            response = urllib2.urlopen(req)
            resultat_json = response.read()
            resultat = json.loads(resultat_json)
            logger.info("Added to HootSuite a event " + title + " " + json.dumps(resultat))
        except urllib2.HTTPError, error:
            contents = error.read()
            resultat = json.loads(contents)
            logger.error("Error on added a Hootsuite event " + title + " " + json.dumps(resultat))
