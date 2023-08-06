""" See COPYING for license information """
from softlayer_messaging.compat import json
import softlayer_messaging.resource


class Queue(softlayer_messaging.resource.Resource):
    def __init__(self, endpoint, name, auth, **kwargs):
        self.name = name
        self.auth = auth
        super(Queue, self).__init__(
            '/'.join((endpoint, 'queues', name)), **kwargs)
        self.headers['Content-Type'] = 'application/json'

    def message(self, message_id):
        return Message(self.url, self.name, message_id, self.auth)

    def request(self, method, *args, **kwargs):
        kwargs['auth'] = self.auth
        resp = super(Queue, self).request(method, *args, **kwargs)
        resp.raise_for_status()
        return resp

    def detail(self):
        return self.get().json

    def modify(self, **kwargs):
        queue = {}
        queue.update(kwargs)
        data = json.dumps(queue)
        r = self.put(data=data)
        return r.json

    def delete(self, force=False, params=None, *args, **kwargs):
        if not params:
            params = {}
        if force:
            params['force'] = 1
        super(Queue, self).delete(params=params, *args, **kwargs)
        return True

    def push(self, body, **kwargs):
        message = {'body': body}
        message.update(kwargs)
        r = self.post("messages", data=json.dumps(message))
        return r.json

    def pop(self, count=1):
        r = self.get('messages', params={'batch': count})
        return r.json

    def __repr__(self):
        return '<Queue [%s]>' % (self.url)


class Message(softlayer_messaging.resource.Resource):
    def __init__(self, endpoint, queue_name, id, auth, **kwargs):
        self.queue_name = queue_name
        self.id = id
        self.auth = auth
        super(Message, self).__init__(
            '/'.join((endpoint, 'messages', id)), **kwargs)

    def request(self, method, *args, **kwargs):
        kwargs['auth'] = self.auth
        resp = super(Message, self).request(method, *args, **kwargs)
        resp.raise_for_status()
        return resp

    def delete(self, *args, **kwargs):
        super(Message, self).delete(*args, **kwargs)
        return True

    def __repr__(self):
        return '<Message [%s]>' % (self.url)
