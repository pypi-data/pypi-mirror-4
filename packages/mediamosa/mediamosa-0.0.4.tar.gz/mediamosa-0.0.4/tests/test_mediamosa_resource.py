import datetime
import unittest

from minimock import Mock, mock, TraceTracker

from mediamosa.resources import Asset, MediaMosaResource
from mediamosa.api import MediaMosaAPI


class TestMediaMosaResource(unittest.TestCase):
    """Tests the generic functionality of a MediaMosaResource. This is
    done using the Asset object as concrete implementation.
    """

    def setUp(self):
        self.api = MediaMosaAPI('http://video.example.com')
        self.tt = TraceTracker()
        mock('self.api.session', tracker=self.tt)
        self.response = Mock('requests.Response')
        self.response.status_code = 200
        self.api.session.get.mock_returns = self.response

        self.item_dict = {
            u'provider_id': '', u'is_unappropriate': u'FALSE',
            u'videotimestampmodified': u'2012-07-05 11:34:35',
            u'app_id': u'2', u'is_favorite': u'FALSE',
            u'has_streamable_mediafiles': u'TRUE', u'viewed': u'4',
            u'asset_id': u'g1QkoSmSeHdWfGkMKlOlldLn',
            u'ega_still_url': '', u'granted': u'TRUE', u'played': u'1',
            u'mediafile_duration': u'00:00:52.20',
            # u'videotimestamp': u'2012-07-05 11:34:01', # cleared it for partial
            u'vpx_still_url': u'http://filvideod.ugent.be/media/17/Z/Z14cWALWKmfTRjTUKhhQQLv2.jpeg',
            u'owner_id': u'krkeppen', u'is_empty_asset': u'FALSE',
            u'play_restriction_end': '', u'asset_property_is_hidden': u'FALSE',
            u'dublin_core': {u'publisher': u'Kristof Keppens',
            u'rights': u'Kristof Keppens', u'description': u'test',
            u'language': u'nl', u'creator': u'Kristof Keppens',
            u'format': u'streaming video', u'coverage_spatial': '',
            u'date': '', u'relation': '', u'source': u'ugent',
            u'contributor': u', ', u'title': u'test sintel 2',
            u'identifier': '', u'type': u'video', u'coverage_temporal': '',
            u'subject': u'test'}, u'reference_id': '', u'isprivate': u'TRUE',
            u'qualified_dublin_core': {u'isformatof': '',
            u'description_abstract': '', u'license': '', u'created': '',
            u'issued': '', u'rightsholder': '', u'hasformat': '',
            u'title_alternative': '', u'format_medium': '',
            u'format_extent': '', u'isreferencedby': ''},
            u'mediafile_container_type': u'matroska;webm',
            u'is_unappropiate': u'FALSE', u'is_external': u'FALSE',
            u'is_protected': u'FALSE', u'play_restriction_start': '',
            u'group_id': ''}

    # _mmmeta.state

    def test_create_empty_asset(self):
        """Tests if an empty asset can be created"""
        a = Asset('g1QkoSmSeHdWfGkMKlOlldLn')
        self.assertEqual(a._mmmeta.state, MediaMosaResource.STATE.EMPTY)

    def test_create_partial_asset(self):
        """Tests if a partially pre-filled asset can be created"""
        a = Asset.fromdict(self.item_dict)
        self.assertEqual(a._mmmeta.state, MediaMosaResource.STATE.PARTIAL)

    def test_create_full_asset(self):
        """Tests if an fully pre-filled asset can be created"""
        a = Asset.fromdict(self.item_dict, full=True)
        self.assertEqual(a._mmmeta.state, MediaMosaResource.STATE.FULL)

    # _mmmeta.api

    def test_create_connected_asset(self):
        """Tests if a connected asset can be created"""
        a = Asset('g1QkoSmSeHdWfGkMKlOlldLn', api=self.api)
        self.assertTrue(a.is_connected())

    def test_create_unconnected_asset(self):
        """Tests if an unconnected asset can be created"""
        a = Asset('g1QkoSmSeHdWfGkMKlOlldLn')
        self.assertFalse(a.is_connected())

    # accessing supplied data

    def test_can_access_asset_data(self):
        """Tests if pre-filled data can be accessed"""
        a = Asset.fromdict(self.item_dict)
        self.assertEquals(a.asset_id, 'g1QkoSmSeHdWfGkMKlOlldLn')
        self.assertIsInstance(a.is_favorite, bool)
        self.assertIsInstance(a.videotimestampmodified, datetime.datetime)
        self.assertRaises(Exception, a.some_unexisting_attribute)
        self.assertEqual(a._mmmeta.state, MediaMosaResource.STATE.PARTIAL)

    # accessing unsupplied data

    def test_accessing_empty_asset(self):
        """Tests if an empty asset will automatically fill itself if
        queried"""
        # setup
        self.response.content = open('tests/data/get_asset_id_response.xml')\
                                    .read()
        # test
        asset = Asset('g1QkoSmSeHdWfGkMKlOlldLn', api=self.api)
        # validate
        self.assertIsInstance(asset.is_favorite, bool)
        self.assertNotEquals(self.tt.dump(), '')
        self.tt.clear()
        self.assertIsInstance(asset.videotimestamp, datetime.datetime)
        self.assertEquals(self.tt.dump(), '')
        self.assertRaises(Exception, asset.some_unexisting_attribute)
        self.assertEqual(asset._mmmeta.state, MediaMosaResource.STATE.FULL)

    def test_accessing_partial_asset(self):
        """Tests if a partial asset will automatically fill itself if
        queried"""
        # setup
        self.response.content = open('tests/data/get_asset_id_response.xml')\
                                    .read()
        # test
        asset = Asset.fromdict(self.item_dict, api=self.api, full=False)
        # validate
        self.assertIsInstance(asset.is_favorite, bool)
        self.assertEquals(self.tt.dump(), '')
        self.assertIsInstance(asset.videotimestamp, datetime.datetime)
        self.assertNotEquals(self.tt.dump(), '')
        self.assertRaises(Exception, asset.some_unexisting_attribute)
        self.assertEqual(asset._mmmeta.state, MediaMosaResource.STATE.FULL)
