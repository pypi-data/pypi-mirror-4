import requests
import json

API_ROOT = 'https://rest.gadventures.com'
API_PROXY = ''
APPLICATION_KEY = ''

class ApiBase(object):
    def _request(self, uri, method, data=None, options=None):
        """
        Make an HTTP request to a target API method with proper headers.
        """
        assert method in ['GET'], "Only 'GET' is allowed."

        # Support supplying a full url
        if '://' in uri:
            url = uri
        else:
            url = API_ROOT + uri

        headers = {'Content-Type': 'application/json', 'X-Application-Key': APPLICATION_KEY}

        if API_PROXY:
            headers.update({'X-Api-Proxy': API_PROXY})

        requests_call = getattr(requests, method.lower())

        request = requests_call(url, headers=headers, data=data, params=options)

        if request.status_code in (requests.codes.ok, requests.codes.created,
                requests.codes.accepted):
            response_dict = json.loads(request.text)
            return response_dict
        else:
            request.reason = request.text
            return request.raise_for_status()

class ApiObject(ApiBase):
    def __init__(self, resource_name, data_dict=None):
        self._resource_name = resource_name
        self._object_id = None

        self._data_dict = {}
        if data_dict:
            self._populate_from_dict(data_dict)

    def set(self, data_dict):
        self._data_dict.update(data_dict)

    def _populate_from_dict(self, data_dict):
        if 'id' in data_dict:
            self._object_id = data_dict['id']

        self._data_dict.update(data_dict)

    def as_dict(self):
        update_fields = self._data_dict.keys()
        properties = [(k, v) for k, v in self._data_dict.items()
                        if not k.startswith('_') and k in update_fields]
        return dict(properties)

    def as_json(self):
        return json.dumps(self.as_dict())

    def __repr__(self):
        return '<{}: {}>'.format(self._resource_name, self._object_id)

class Query(ApiBase):
    def __init__(self, resource_name):
        self._resource_name = resource_name
        self._object_id = None
        self._parent = None
        self._where = {}

    def get(self, object_id):
        self._object_id = object_id
        return self._fetch_one()

    def parent(self, resource_name, resource_id):
        self._parent = (resource_name, resource_id)
        return self

    def eq(self, name, value):
        self._where[name] = value
        return self

    def fetch(self):
        return self._fetch_all()

    def _get_uri(self):
        if self._object_id:
            return '/{0}/{1}'.format(self._resource_name, self._object_id)
        else:
            if self._parent:
                parent_name, parent_id = self._parent
                return '/{0}/{1}/{2}'.format(parent_name, parent_id,
                        self._resource_name)
            else:
                return '/{0}'.format(self._resource_name)

    def _fetch_one(self):
        uri = self._get_uri()
        response_dict = self._request(uri, 'GET')
        return ApiObject(self._resource_name, response_dict)

    def _fetch_all(self, uri=None):
        '''
        ``uri``
            For following paginated results or otherwise pregenerated uri's
            from the response itself.
        '''
        if not uri:
            uri = self._get_uri()

        options = {}
        if self._where:
            options.update(self._where)

        response_dict = self._request(uri, 'GET', options=options)
        for result in response_dict['results']:
            yield ApiObject(self._resource_name, result)

        # Results are paginated so continue with another query
        for link in response_dict.get('links', []):
            if link['rel'] != 'next':
                continue
            for result in self._fetch_all(link['href']):
                yield result

