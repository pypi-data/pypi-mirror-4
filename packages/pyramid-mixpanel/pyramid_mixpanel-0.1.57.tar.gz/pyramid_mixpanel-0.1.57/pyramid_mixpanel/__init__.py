# -*- coding: utf-8 -*-
import json
import base64
import logging
from decimal import Decimal
from datetime import datetime, date

import requests
from pyramid.settings import asbool
from zope.interface import implementer
from zope.interface import Attribute, Interface

log = logging.getLogger(__name__)


def includeme(config):
    log.info('Including pyramid_mixpanel')
    if asbool(config.registry.settings.get("mixpanel.enabled", True)):
        log.info('Tracking enabled.')
        utility = MixpanelUtility(config.registry.settings)
    else:
        log.info('Tracking disabled -- using dummy utility.')
        utility = DummyMixpanelUtility()
    config.registry.registerUtility(utility)
    config.commit()


class _CustomJSONEncoder(json.JSONEncoder):
    """Custom encoder that supports extra types.

    Supported types: date, datetime, Decimal.
    """

    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()

        if isinstance(o, Decimal):
            return _number_str(o)

        return super(_CustomJSONEncoder, self).default(o)


class _number_str(float):
    # kludge to have decimals correctly output as JSON numbers;
    # converting them to strings would cause extra quotes

    def __init__(self, o):
        self.o = o

    def __repr__(self):
        return str(self.o)


def get_mixpanel_utility(request):
    """Retrieve mixpanel utility from the registry."""
    return request.registry.getUtility(IMixpanelUtility)


class IMixpanelUtility(Interface):
    """Utility to track events & people on Mixpanel service."""

    token = Attribute("""Mixpanel token""")

    def track(event, properties):
        """Track an event and its properties.

        *event* is a string naming the category to use for this data.
        *properties* is a dictionary.

        This accepts datatypes that a default JSON encoder can encode,
        plus date, datetime and Decimal objects.
        """

    def people_track(distinct_id, properties, action=u'$set', ip=u'0'):
        """Create or update user in Mixpanel People.

        *distinct_id* must be a string and *properties* a dictionary.
        See Mixpanel People documentation for info about special keys.

        The same function is used to create the user, update the last
        login and update the transaction information, because we can't
        know for sure when an update can be done instead of a create,
        so we always send all the information.  This has the side
        effect of possibly updating info that have been refreshed with
        real-time update.

        If *action* is ``"$set"`` (default), any properties you specify
        will replace existing values in mixpanel's DB.

        If *action* is ``"$append"`` and *properties*'s only key is
        ``"$transactions"``, the transaction in *properties* will be
        added to the list of transactions for this user in the mixpanel DB.

        Note that Mixpanel only supports ``"$append"`` for transactions,
        and that transactions must be of the form
        ``{"$time": iso_datetime, "$amount": number}``.

        *ip* is the IP address of the client.  The default value of '0'
        will cause Mixpanel to store nothing; without value, the server
        IP would be used.  This field is necessary to detect the user's
        location.  If the address is malformed in any way (e.g. it's a
        comma-separated pair of IPs because the client is behind a proxy),
        Mixpanel just ignores it.
        """


@implementer(IMixpanelUtility)
class MixpanelUtility(object):

    def __init__(self, settings):
        self.token = settings['mixpanel.token']

    def track(self, event, properties):
        url = "https://api.mixpanel.com/track"
        if u'token' not in properties:
            properties[u'token'] = self.token

        try:
            params = {'event': event, 'properties': properties}
            data = base64.b64encode(json.dumps(params, cls=_CustomJSONEncoder))
            # TODO POST is also accepted and better HTTP, use it
            response = requests.get(url, params={'data': data})
            response.raise_for_status()
        except Exception:
            log.exception('mixpanel track event exception: event %s; '
                          'properties: %s', event, properties)

    def people_track(self, distinct_id, properties, action=u'$set', ip=u'0'):
        try:
            data = base64.b64encode(json.dumps({
                u'$token': self.token,
                u'$distinct_id': distinct_id,
                u'$ip': ip,
                action: properties,
            }, cls=_CustomJSONEncoder))

            response = requests.post('https://api.mixpanel.com/engage/',
                                     {'data': data})
            response.raise_for_status()
        except Exception:
            log.exception('mixpanel people tracking error')
            return

        result = response.content  # '1' means OK
        if result == '0':
            log.error('mixpanel people tracking returned error status')
        elif result != '1':
            log.warning('unknown status returned by mixpanel people '
                        'tracking: %r', result)


@implementer(IMixpanelUtility)
class DummyMixpanelUtility(object):
    """Dummy mixpanel utility -- it does nothing.

    Use it as a replacement for the regular mixpanel utility when
    running tests.
    """

    token = 'dummy token'

    def track(self, event, properties):
        log.debug('Tracking event "%s" with properties %s', event, properties)

    def people_track(self, distinct_id, properties, action=u'$set', ip=u'0'):
        log.debug(
            'Tracking person "%s" with properties %s', distinct_id, properties)
