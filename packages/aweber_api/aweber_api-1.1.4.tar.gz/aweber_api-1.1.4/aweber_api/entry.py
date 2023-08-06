import aweber_api
from aweber_api.response import AWeberResponse
from aweber_api.data_dict import DataDict

from urllib import urlencode


class AWeberEntry(AWeberResponse):
    """
    Represents a single entry in the AWeber API data heirarchy, such as one
    specific account, list, web form, etc.  Built on data that is returned
    from an id-ed URI, such as:
        /accounts/XXXX
        /accounts/XXXX/lists/XXXX
    Can also be generated from the data in the entries array of a collection
    object, which is identical to the data return from the URI for that
    specific entry.

    Provides direct access to properties in the response, such as self.id
    """

    def __init__(self, url, data, adapter):
        self._data = {}
        self._diff = {}
        AWeberResponse.__init__(self, url, data, adapter)
        self._child_collections = {}

    def __setattr__(self, key, value):
        if not key == '_data' and key in self._data:
            self._data[key] = value
            self._diff[key] = value
            return value
        return AWeberResponse.__setattr__(self, key, value)

    def delete(self):
        """Invoke the API method to DELETE* this entry resource.

        * Note: Not all entry resources are eligible to be DELETED, please
                refer to the AWeber API Reference Documentation at
                https://labs.aweber.com/docs/reference/1.0 for more
                details on which entry resources may be deleted.
        """
        self.adapter.request('DELETE', self.url, response='status')
        return True

    def move(self, list_, **kwargs):
        """Invoke the API method to MOVE an entry resource to a
           different List.

        Note: Not all entry resources are eligible to be moved, please
              refer to the AWeber API Reference Documentation at
              https://labs.aweber.com/docs/reference/1.0 for more
              details on which entry resources may be moved and if there
              are any requirements for moving that resource.
        """
        params = {'ws.op': 'move',
                  'list_link': list_.self_link}
        params.update(kwargs)
        response = self.adapter.request('POST', self.url, params,
                                        response='headers')

        new_resource = response['location']
        self._diff = {}
        self._data = self.adapter.request('GET', new_resource)
        return True

    def save(self):
        self.adapter.request('PATCH', self.url, self._diff, response='status')
        self._diff = {}
        return True

    def get_activity(self):
        """Invoke the API method to return all Subscriber activity.

        * Note: This method only works on Subscriber Entry resources.
                refer to the AWeber API Reference Documentation at
                https://labs.aweber.com/docs/reference/1.0#subscriber
                for more details on how to call this method.
        """
        self._method_for('subscriber')
        params = {'ws.op': 'getActivity'}
        query_string = urlencode(params)
        url = '{0.url}?{1}'.format(self, query_string)
        data = self.adapter.request('GET', url)

        collection = aweber_api.AWeberCollection(url, data, self.adapter)
        collection._data['total_size'] = self._get_total_size(url)
        return collection

    def findSubscribers(self, **kwargs):
        """Invoke the API method to find all subscribers on all Lists

        * Note: This method only works on Account Entry resources and
                requires access to subscriber information. please
                refer to the AWeber API Reference Documentation at
                https://labs.aweber.com/docs/reference/1.0#account
                for more details on how to call this method.
        """
        self._method_for('account')
        params = {'ws.op': 'findSubscribers'}
        params.update(kwargs)
        query_string = urlencode(params)
        url = '{0.url}?{1}'.format(self, query_string)

        data = self.adapter.request('GET', url)
        collection = aweber_api.AWeberCollection(url, data, self.adapter)
        collection._data['total_size'] = self._get_total_size(url)
        return collection

    def _get_total_size(self, uri, **kwargs):
        """Get actual total size number from total_size_link."""
        total_size_uri = '{0}&ws.show=total_size'.format(uri)
        return int(self.adapter.request('GET', total_size_uri))

    def get_parent_entry(self):
        """Return the parent entry of this entry or None if no parent exists.

        Example:
            calling get_parent_entry on a SubscriberEntry will return the List
            Entry that SubscriberEntry belongs to.  For more information on
            the AWeber API and how resources are arranged, refer to:
            https://labs.aweber.com/docs/reference/1.0
        """
        url_parts = self.url.split('/')
        size = len(url_parts)
        url = self.url[:-len(url_parts[size-1])-1]
        url = url[:-len(url_parts[size-2])-1]

        if url == '':
            return None

        data = self.adapter.request('GET', url)
        return AWeberEntry(url, data, self.adapter)

    def get_web_forms(self):
        self._method_for('account')
        data = self.adapter.request('GET',
                                    "{0}?ws.op=getWebForms".format(self.url))
        return self._parseNamedOperation(data)

    def get_web_form_split_tests(self):
        self._method_for('account')
        data = self.adapter.request(
            'GET',
            "{0}?ws.op=getWebFormSplitTests".format(self.url),
        )
        return self._parseNamedOperation(data)

    def _child_collection(self, attr):
        if not attr in self._child_collections:
            url = "{0}/{1}".format(self.url, attr)
            self._child_collections[attr] = self.load_from_url(url)
        return self._child_collections[attr]

    def __getattr__(self, attr):
        if attr in self._data:
            if isinstance(self._data[attr], dict):
                return DataDict(self._data[attr], attr, self)
            return self._data[attr]
        elif attr in self.collections_map[self.type]:
            return self._child_collection(attr)
        else:
            raise AttributeError(attr)
