from math import floor
from urlparse import parse_qs
from urllib import urlencode

import aweber_api
from aweber_api.response import AWeberResponse


class AWeberCollection(AWeberResponse):
    """
    Represents a collection of similar objects.  Encapsulates data that is
    found at the base URI's for a given object type, ie:
        /accounts
        /accounts/XXX/lists
    Parses the data from the response and provides basic sequence like
    operations, such as iteration and indexing to access the entries that
    are contained in this collection.
    """
    page_size = 100

    def __init__(self, url, data, adapter):
        self._entry_data = {}
        self._current = 0

        AWeberResponse.__init__(self, url, data, adapter)
        self._key_entries(self._data)

    def get_by_id(self, id):
        """
        Returns an entry from this collection, as found by its actual
        AWeber id, not its offset.  Will actually request the data from
        the API.
        """
        return self.load_from_url("{0}/{1}".format(self.url, id))

    def _key_entries(self, response):
        count = 0
        for entry in response['entries']:
            self._entry_data[count+response['start']] = entry
            count += 1

    def _load_page_for_offset(self, offset):
        page = self._get_page_params(offset)
        response = self.adapter.request('GET', self.url, page)
        self._key_entries(response)

    def _get_page_params(self, offset):
        next_link = self._data.get('next_collection_link', None)
        if next_link is None:
            """no more parameters in page!"""
            raise StopIteration

        url, query = next_link.split('?')
        query_parts = parse_qs(query)
        self.page_size = int(query_parts['ws.size'][0])
        page_number = int(floor(offset / self.page_size))
        start = page_number * self.page_size
        return { 'ws.start' : start, 'ws.size' : self.page_size }

    def create(self, **kwargs):
        params = {'ws.op': 'create'}
        params.update(kwargs)

        response = self.adapter.request('POST', self.url, params,
            response='headers')

        resource_url = response['location']
        data = self.adapter.request('GET', resource_url)
        return aweber_api.AWeberEntry(resource_url, data, self.adapter)

    def find(self, **kwargs):
        params = {'ws.op': 'find'}
        params.update(kwargs)
        query_string = urlencode(params)
        url = '{0.url}?{1}'.format(self, query_string)
        data = self.adapter.request('GET', url)

        collection = AWeberCollection(url, data, self.adapter)
        collection._data['total_size'] = self._get_total_size(url)
        return collection

    def _get_total_size(self, uri, **kwargs):
        """Get actual total size number from total_size_link."""
        total_size_uri = '{0}&ws.show=total_size'.format(uri)
        return int(self.adapter.request('GET', total_size_uri))

    def get_parent_entry(self):
        """Return a collection's parent entry or None."""
        url_parts = self.url.split('/')

        #If top of tree - no parent entry
        if len(url_parts) <= 3:
            return None
        size = len(url_parts)

        #Remove collection id and slash from end of url
        url = self.url[:-len(url_parts[size-1])-1]
        data = self.adapter.request('GET', url)
        try:
            entry = aweber_api.AWeberEntry(url, data, self.adapter)
        except TypeError:
            return None

        return entry

    def _create_entry(self, offset):
        data = self._entry_data[offset]
        url = data['self_link'].replace(aweber_api.API_BASE, '')
        self._entries[offset] = aweber_api.AWeberEntry(url, data,
                self.adapter)

    def __len__(self):
        return self.total_size

    def __iter__(self):
        return self

    def next(self):
        if self._current < self.total_size:
            self._current += 1
            return self[self._current-1]
        self._current = 0
        raise StopIteration

    def __getitem__(self, offset):
        if offset < 0 or offset >= self._data['total_size']:
            raise ValueError('Offset {0} does not exist'.format(offset))

        if not offset in self._entries:
            if not offset in self._entry_data:
                self._load_page_for_offset(offset)
            self._create_entry(offset)
        return self._entries[offset]

