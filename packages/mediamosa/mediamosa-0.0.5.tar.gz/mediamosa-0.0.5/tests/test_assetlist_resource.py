import unittest

from minimock import Mock, mock, TraceTracker

from mediamosa.resources import AssetList, Asset
from mediamosa.api import MediaMosaAPI


class TestAssetListResource(unittest.TestCase):

    def setUp(self):
        self.api = MediaMosaAPI('http://video.example.com')
        self.tt = TraceTracker()
        mock('self.api.session', tracker=self.tt)
        self.response = Mock('requests.Response')
        self.response.status_code = 200
        self.api.session.get.mock_returns = self.response

    def _get_asset_list(self, amount, total, offset):
        response = open('tests/data/get_asset_list_response.xml').read()
        asset_item = open('tests/data/asset_item.xml').read()

        asset_items = ''
        for i in xrange(offset, offset + amount):
            asset_items += asset_item.replace('{{item_id}}', str(i))

        return response.replace('{{item_count}}', str(amount))\
                       .replace('{{item_count_total}}', str(total))\
                       .replace('{{item_offset}}', str(offset))\
                       .replace('{{asset_items}}', asset_items)

    def test_getting_paginated_assetlist(self):
        """Test fetching an asset list from the api."""
        # setup
        amount = 10
        total_items = 42
        offset = 0
        self.response.content = self._get_asset_list(
            amount, total_items, offset)
        # test
        asset_list = self.api.asset_list()
        # validate
        self.assertIsInstance(asset_list, AssetList)
        self.assertEqual(len(asset_list), total_items)
        self.assertEqual(asset_list._api, self.api)

    def test_fetch_page(self):
        # setup
        amount = 10
        total_items = 42
        offset = 10  # we have assets 10 to 19
        self.response.content = self._get_asset_list(
            amount, total_items, offset)
        asset_list = self.api.asset_list()

        # test first ten
        self.response.content = self._get_asset_list(
            10, total_items, 0)
        asset_list._fetch_page(0, 10)
        self.assertEqual(len(asset_list), total_items)
        self.assertEqual(asset_list.page_size(), 10)
        self.assertEqual(asset_list.page_offset(), 0)

        # test last two
        self.response.content = self._get_asset_list(
            2, total_items, 40)
        asset_list._fetch_page(40, 10)
        self.assertEqual(len(asset_list), total_items)
        self.assertEqual(asset_list.page_size(), 2)
        self.assertEqual(asset_list.page_offset(), 40)

    def test_getting_assets(self):
        """Test whether AssetList will fetch a new page from api if a
        query is done outside the view
        """
        # setup
        amount = 10
        total_items = 42
        offset = 10  # we have assets 10 to 19
        self.response.content = self._get_asset_list(
            amount, total_items, offset)

        asset_list = self.api.asset_list()

        # test INSIDE current page
        asset = asset_list[10]
        self.assertIsInstance(asset, Asset)
        asset = asset_list[19]
        self.assertIsInstance(asset, Asset)

        # test BEFORE current page
        self.response.content = self._get_asset_list(
            10, total_items, 0)

        asset = asset_list[0]
        self.assertIsInstance(asset, Asset)
        asset = asset_list[9]
        self.assertIsInstance(asset, Asset)

        # test AFTER current page
        self.response.content = self._get_asset_list(
            10, total_items, 15)

        asset = asset_list[20]
        self.assertIsInstance(asset, Asset)

        # test Out of Bounds
        self.assertRaises(Exception, asset_list.__getitem__, -1)
        self.assertRaises(Exception, asset_list.__getitem__, 42)

    def test_iterating_over_paginated_assetlist(self):
        # setup
        total_items = 42
        self.response.content = self._get_asset_list(
            total_items, total_items, 0)
        asset_list = self.api.asset_list()
        # test
        count = 0
        for asset in asset_list:
            count += 1
        # validate
        self.assertEqual(count, total_items)
