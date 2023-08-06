""" See COPYING for license information """
from softlayer_messaging.compat import json
import softlayer_messaging.resource
import softlayer_messaging.queue
import softlayer_messaging.topic
from softlayer_messaging.auth import QueueAuth
import requests


class QueueClient(softlayer_messaging.resource.Resource):
    def __init__(self, endpoint, account, **kwargs):
        self.account = account
        self.endpoint = endpoint
        self.auth = None
        super(QueueClient, self).__init__(
            '/'.join((endpoint, 'v1', account)), **kwargs)
        self.headers['Content-Type'] = 'application/json'

    def authenticate(self, username, api_key, auth_token=None):
        auth_endpoint = '/'.join(
            (self.endpoint, 'v1', self.account, 'auth'))
        self.auth = QueueAuth(auth_endpoint, username, api_key,
                              auth_token=auth_token)
        self.auth.auth()

    def ping(self):
        try:
            r = requests.get('%s/v1/ping' % self.endpoint)
        except:
            return False
        return 200 <= r.status_code <= 299

    def request(self, method, *args, **kwargs):
        kwargs['auth'] = self.auth
        resp = super(QueueClient, self).request(method, *args, **kwargs)
        resp.raise_for_status()
        return resp

    def queue(self, name):
        return softlayer_messaging.queue.Queue(self.url, name, self.auth)

    def topic(self, name):
        return softlayer_messaging.topic.Topic(self.url, name, self.auth)

    def queues(self, tags=None):
        params = {}
        if tags:
            params['tags'] = ','.join(tags)
        r = self.get('queues', params=params)
        return r.json

    def topics(self, tags=None):
        params = {}
        if tags:
            params['tags'] = ','.join(tags)
        r = self.get('topics', params=params)
        return r.json

    def create_queue(self, name, **kwargs):
        queue = {}
        queue.update(kwargs)
        data = json.dumps(queue)
        r = self.put("queues/%s" % (name, ), data=data)
        return r.json

    def create_topic(self, name, **kwargs):
        topic = {}
        topic.update(kwargs)
        data = json.dumps(topic)
        r = self.put("topics/%s" % (name, ), data=data)
        return r.json

    def stats(self, period='hour'):
        r = self.get("stats/%s" % (period, ))
        return r.json

    def __repr__(self):
        return '<QueueClient [%s]>' % (self.url)
