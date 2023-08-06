"""
SoftLayer Message Queue Python Client

Example Usage:
    import softlayer_messaging

    client = softlayer_messaging.get_client('YOUR_ACCOUNT', 'YOUR_USERNAME',
        api_key='YOUR_API_KEY', endpoint='https://dal05.mq.softlayer.net/')

    print(client.queues())


See COPYING for license information
"""
from softlayer_messaging.errors import *
from softlayer_messaging.constants import ENDPOINTS, VERSION
from softlayer_messaging.client import QueueClient

__version__ = VERSION


def get_client(account, endpoint=None, datacenter='dal05', network='public'):
    """ Returns a softlayer_messaging client. """
    if not endpoint:
        endpoint = "https://%s" % ENDPOINTS[datacenter][network]
    return QueueClient(endpoint, account)
