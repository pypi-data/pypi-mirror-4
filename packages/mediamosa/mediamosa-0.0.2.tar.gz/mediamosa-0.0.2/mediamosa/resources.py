import datetime


class MediaMosaResource(object):

    class STATE(object):
        EMPTY = 0
        PARTIAL = 1
        FULL = 2

    def __init__(self, resource_id, api=None):
        """Initializes an empty resource.
        """
        self.id = resource_id
        self.data = {}
        self._mmmeta = self._Meta()
        self._mmmeta.api = api
        self._mmmeta.state = self.STATE.EMPTY

    def __getattr__(self, attr):
        """Looks up an attribute in the data dictionary. It will query
        the api if there is no data available.
        """
        # ignore private attributes
        if attr.startswith('_'):
            raise AttributeError

        # return it if it already exists
        if attr in self.data:
            return self.handle(attr, self.data.get(attr))

        # do a lookup for partials and upgrade to full
        if not self._mmmeta.state == self.STATE.FULL and self.is_connected():
            new_resource = self.fetch_resource_from_api(self.id)
            # add received data to resource and change is_empty state
            self.data = new_resource.data
            self._mmmeta.state = self.STATE.FULL
            # retry lookup
            return self.__getattr__(attr)

    def handle(self, attr, value):
        """Will translate the API value to its python equivalent. This
        depends on the BOOLEANS and DATETIMES tuples defined in the
        concrete MediaMosa resource.
        """
        if attr in self.BOOLEANS:
            return value == u'TRUE'
        elif attr in self.DATETIMES:
            return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            return value

    @classmethod
    def fromdict(cls, dct, api=None, full=False):
        """Creates an MediaMosaResource from a resource description
        received from the MediaMosaAPI."""
        res_id = dct.get(cls.RESOURCE_ID_KEY)
        resource = cls(res_id)
        resource.data = dct
        if full:
            resource._mmmeta.state = cls.STATE.FULL
        else:
            resource._mmmeta.state = cls.STATE.PARTIAL
        resource._mmmeta.api = api
        return resource

    def is_connected(self):
        return self._mmmeta.api is not None

    class _Meta(object):
        state = None
        api = None


class Mediafile(MediaMosaResource):
    RESOURCE_ID_KEY = 'mediafile_id'
    BOOLEANS = (
        'is_original_file', 'is_streamable', 'is_downloadable',
        'response_metafile_available', 'is_protected', 'is_inserted_md',
        'is_hinted', 'response_plain_available', 'response_object_available',
        'is_still',
    )
    DATETIMES = (
        'created', 'changed',
    )

    class FORMATS(object):
        DOWNLOAD = 'download'
        METAFILE = 'metafile'
        OBJECT = 'object'
        STILL = 'still'
        PLAIN = 'plain'
        CUPERTINE = 'cupertino'
        RSTP = 'rstp'
        SILVERLIGHT = 'silverlight'

    def fetch_resource_from_api(self, res_id):
        """Performs the api query necessary to retrieve the mediamosa resource.
        """
        return self._mmmeta.api.mediafile(self.id)

    def __repr__(self):
        return "<mediamosa.resources.Mediafile (%s) %s>" % \
            (self.file_extension, self.id)

    def play(self, format=None):
        play_info = self._mmmeta.api.play(
            self, user_id='pyUser',
            response=format or self.FORMATS.OBJECT)
        if play_info:
            return play_info.get('output')
        return None


class Asset(MediaMosaResource):
    RESOURCE_ID_KEY = 'asset_id'
    BOOLEANS = (
        'is_unappropriate', 'is_favorite', 'has_streamable_mediafiles',
        'granted', 'is_empty_asset', 'asset_property_is_hidden',
        'isprivate', 'is_unappropiate', 'is_external', 'is_protected',
    )
    DATETIMES = (
        'videotimestampmodified', 'videotimestamp',
    )

    def fetch_resource_from_api(self, res_id):
        """Performs the api query necessary to retrieve the mediamosa resource.
        """
        return self._mmmeta.api.asset(self.id)

    def source(self):
        """Returns the mediafile describing the source
        """
        mediafiles = self.list_mediafiles()
        for mediafile in mediafiles:
            if mediafile.is_original_file:
                return mediafile
        return None

    def list_mediafiles(self):
        """Returns a list of mediafiles associated with this asset
        """
        return [Mediafile.fromdict(dct,
            api=self._mmmeta.api, full=False) for dct in self.mediafiles]

    def get_mediafile(self, extension='mp4'):
        """Returns the mediafile with a specific extension. If the
        original is of extension it will only return it if there is no
        re-encoded version with the same extension.
        """
        mediafiles = self.list_mediafiles()
        original = None
        for mediafile in mediafiles:
            if mediafile.is_original_file\
                 and mediafile.file_extension == extension:
                original = mediafile

            elif mediafile.file_extension == extension\
                 and not mediafile.is_original_file:
                return mediafile

        return original

    def __repr__(self):
        return "<mediamosa.resources.Asset %s>" % self.id


class AssetList(list):

    DEFAULT_LIMIT = 10

    def __init__(self, headers, body, api=None):
        self._api = api
        self.headers = headers
        self.body = body
        self._update_location_info()
        # add items to the body
        super(AssetList, self).__init__(body)

    def page_offset(self):
        return self.headers.get('item_offset')

    def page_size(self):
        return self.headers.get('item_count')

    def _update_location_info(self):
        """Updates offset and size information based on headers
        information
        """
        self.offset = self.headers.get('item_offset', 0)
        self.item_size = self.headers.get('item_count', 0)

    def _fetch_page(self, offset, limit=None):
        """Fetches another page from the api
        """
        # query new list of items
        new_asset_list = self._api.asset_list(offset=offset,
            limit=limit or self.DEFAULT_LIMIT)
        # update header info and pointers
        self.headers = new_asset_list.headers
        self._update_location_info()
        # repopulate parent list object
        super(AssetList, self).__init__(new_asset_list.body)

    def __getitem__(self, index):
        # convert index relative to internal list
        relative_index = index - self.offset

        # not an integer
        if type(index) != int:
            raise TypeError("Index not an integer")

        # out of bounds check
        if index < 0 or index >= len(self):
            raise IndexError("Index out of range")

        # check if before or after current page
        if (relative_index < 0) or (relative_index > (self.item_size - 1)):
            # fetch the page containing the index
            self._fetch_page(index)
            # retry
            return self.__getitem__(index)

        # located in current page.
        else:
            return super(AssetList, self).__getitem__(relative_index)

    def __getslice__(self, i, j):
        # call the required slice from the API.
        self._fetch_page(i, j - i)
        return super(AssetList, self).__getslice__(0, j - i)

    def __iter__(self):
        self.index = -1
        return self

    def next(self):
        self.index += 1
        if -1 < self.index < len(self):
            return self[self.index]
        else:
            raise StopIteration

    def __len__(self):
        """Returns the total amount of assets, not simple the loaded ones.
        """
        return int(self.headers.get('item_count_total', 0))
