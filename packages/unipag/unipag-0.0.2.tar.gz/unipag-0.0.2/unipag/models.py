from .transport import API, json

def objects_from_json(json_content, api_key=None):
    if isinstance(json_content, basestring):
        return objects_from_json(json.loads(json_content))
    elif isinstance(json_content, list):
        return [objects_from_json(obj, api_key) for obj in json_content]
    elif isinstance(json_content, dict):
        obj = json_content.get('object', None)
        if obj:
            id = json_content['id']
            klass = {
                'invoice': Invoice,
                'payment': Payment,
                'event': Event,
                'connection': Connection,
            }.get(obj, UnipagObject)
            return klass(api_key=api_key, id=id).load_from(json_content)
        else:
            return json_content

class UnipagObject(object):

    def __init__(self, api_key=None, id=None, **kwargs):
        self.id = id
        self.api_key = api_key
        self._values = {}
        self.load_from(kwargs)

    def __setattr__(self, key, value):
        if hasattr(self, '_values'):
            self._values[key] = value
        return super(UnipagObject, self).__setattr__(key, value)

    def __repr__(self):
        return '%s id=%s: %s' % (self.__class__.__name__, self.id, self._values)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __eq__(self, other):
        if not hasattr(other, '_values'):
            return False
        if len(self._values) != len(other._values):
            return False
        for k, v in self._values.items():
            if not hasattr(other, k) or self._values[k] != other._values[k]:
                return False
        return True

    @classmethod
    def class_url(cls):
        return '/%ss' % cls.__name__.lower()

    def instance_url(self):
        assert self.id is not None, 'Unable to determine instance URL, '\
                                    'because %s.id is None.' \
                                    '' % self.__class__.__name__
        return '%s/%s' % (self.class_url(), self.id)

    def load_from(self, dikt):
        for k, v in dikt.items():
            if isinstance(v, dict):
                v = objects_from_json(v)
            self.__setattr__(k, v)
        return self

    def reload(self):
        response = API(self.api_key).request('get', self.instance_url())
        return self.load_from(response)

    @classmethod
    def get(cls, id, api_key=None):
        instance = cls(api_key=api_key, id=id)
        return instance.reload()

class CreatableObject(UnipagObject):
    @classmethod
    def create(cls, api_key=None, **kwargs):
        response = API(api_key).request('post', cls.class_url(), params=kwargs)
        return objects_from_json(response)

class UpdatableObject(UnipagObject):
    def save(self):
        if self.id:
            response = API(self.api_key).request(
                'post',
                self.instance_url(),
                params=self._values
            )
        else:
            response = API(self.api_key).request(
                'post',
                self.__class__.class_url(),
                params=self._values
            )
        return self.load_from(response)

class ListableObject(UnipagObject):
    @classmethod
    def list(cls, api_key=None, **kwargs):
        response = API(api_key).request('get', cls.class_url(), kwargs)
        return objects_from_json(response, api_key=api_key)

class RemovableObject(UnipagObject):
    def delete(self):
        response = API(self.api_key).request('delete', self.instance_url())
        return self.load_from(response)

class RestorableObject(UnipagObject):
    def undelete(self):
        response = API(self.api_key).request(
            'post',
            self.instance_url(),
            params={'deleted': False}
        )
        return self.load_from(response)

# -------------- User objects -------------- #

class Invoice(CreatableObject, UpdatableObject, ListableObject,
              RemovableObject, RestorableObject):
    @classmethod
    def create(cls, api_key=None, **kwargs):
        if 'currency' not in kwargs:
            from .defaults import currency
            kwargs.update({'currency': currency})
        return super(Invoice, cls).create(api_key=api_key, **kwargs)

class Payment(CreatableObject, ListableObject):
    def refund(self, amount=None):
        pass

    def cancel(self):
        pass

class Connection(ListableObject):
    pass

class Event(ListableObject):
    pass