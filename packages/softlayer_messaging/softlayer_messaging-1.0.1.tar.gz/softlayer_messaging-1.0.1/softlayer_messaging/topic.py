""" See COPYING for license information """
from softlayer_messaging.compat import json
import softlayer_messaging.resource


class Topic(softlayer_messaging.resource.Resource):
    def __init__(self, endpoint, name, auth, **kwargs):
        self.name = name
        self.auth = auth
        super(Topic, self).__init__(
            '/'.join((endpoint, 'topics', name)), **kwargs)
        self.headers['Content-Type'] = 'application/json'

    def request(self, method, *args, **kwargs):
        kwargs['auth'] = self.auth
        resp = super(Topic, self).request(method, *args, **kwargs)
        resp.raise_for_status()
        return resp

    def detail(self):
        return self.get().json

    def modify(self, **kwargs):
        topic = {}
        topic.update(kwargs)
        data = json.dumps(topic)
        r = self.put(data=data)
        return r.json

    def delete(self, force=False, params=None, *args, **kwargs):
        if not params:
            params = {}
        if force:
            params['force'] = 1
        super(Topic, self).delete(params=params, *args, **kwargs)
        return True

    def push(self, body, **kwargs):
        message = {'body': body}
        message.update(kwargs)
        r = self.post("messages", data=json.dumps(message))
        return r.json

    def subscriptions(self):
        r = self.get('subscriptions')
        return r.json

    def subscription(self, id):
        return Subscription(self.url, id, self.auth)

    def create_subscription(self, type_, **kwargs):
        r = self.post('subscriptions', data=json.dumps(
            {'endpoint_type': type_, 'endpoint': kwargs}))
        return r.json

    def __repr__(self):
        return '<Topic [%s]>' % (self.url)


class Subscription(softlayer_messaging.resource.Resource):
    def __init__(self, endpoint, id, auth, **kwargs):
        self.id = id
        self.auth = auth
        super(Subscription, self).__init__(
            '/'.join((endpoint, 'subscriptions', id)), **kwargs)

    def request(self, method, *args, **kwargs):
        kwargs['auth'] = self.auth
        resp = super(Subscription, self).request(method, *args, **kwargs)
        resp.raise_for_status()
        return resp

    def delete(self, *args, **kwargs):
        super(Subscription, self).delete(*args, **kwargs)
        return True

    def __repr__(self):
        return '<Subscription [%s]>' % (self.url)
