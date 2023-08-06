import unittest

from minimock import Mock, mock, TraceTracker

from mediamosa.resources import Mediafile, MediaMosaResource
from mediamosa.api import MediaMosaAPI


class TestMediafileResource(unittest.TestCase):

    def setUp(self):
        self.api = MediaMosaAPI('http://video.example.com')
        self.tt = TraceTracker()
        mock('self.api.session', tracker=self.tt)
        self.response = Mock('requests.Response')
        self.response.status_code = 200
        self.api.session.get.mock_returns = self.response

        self.item_dict = {u'is_original_file': u'FALSE',
            u'is_streamable': u'FALSE', u'is_downloadable': u'FALSE',
            u'app_id': u'2', u'transcode_inherits_acl': u'TRUE',
            u'tag': '', u'response_metafile_available': u'TRUE',
            u'mediafile_id_source': u'u2ilZNiHdl7iNUdexL7BcFMY',
            u'asset_id': u'g1QkoSmSeHdWfGkMKlOlldLn',
            u'mediafile_id': u'Md2RgaUEVFhfJMeUIbwPOMei',
            u'transcode_profile_id': u'17',
            u'filename': u'Sintel_Trailer1.1080p.DivX_Plus_HD.mp4',
            u'is_protected': u'FALSE', u'ega_stream_url': '',
            u'file_extension': u'mp4', 'metadata': {
            u'is_inserted_md': u'FALSE', u'fps': u'24', u'bpp': u'0.31',
            u'file_duration': u'00:00:52.20', u'colorspace': u'yuv420p',
            u'container_type': u'mov;mp4;m4a;3gp;3g2;mj2', u'height': u'478',
            u'channels': u'stereo', u'width': u'852', u'sample_rate': u'44100',
            u'filesize': u'20543936', u'audio_codec': u'aac',
            u'video_codec': u'h264', u'is_hinted': u'TRUE',
            u'bitrate': u'3012', u'mime_type': u'video/mp4'},
            u'ega_download_url': '', u'ega_play_url': '', u'tool': u'ffmpeg',
            u'response_plain_available': u'TRUE', u'owner_id': u'krkeppen',
            u'response_object_available': u'TRUE',
            u'created': u'2012-07-05 11:38:14',
            u'changed': u'2012-07-05 11:38:14', u'uri': '',
            u'is_still': u'FALSE', u'command':
            u'audiocodec:libfaac;audiobitrate:128000;audiosamplingrate:44100;audiochannels:2;videocodec:libx264;videopreset_quality:slow;videopreset_profile:baseline;2_pass_h264_encoding:2;videobitrate:800000;qmax:17;size:852x480;maintain_aspect_ratio:yes',
            u'group_id': ''}

    def test_getting_full_mediafile(self):
        """Test fetching a full mediafile from the api"""
        # setup
        self.response.content = open('tests/data/get_mediafile_id_response.xml')\
                                    .read()
        # test
        mediafile = self.api.mediafile('g1QkoSmSeHdWfGkMKlOlldLn')
        # validate
        self.assertIsInstance(mediafile, Mediafile)
        self.assertEqual(mediafile._mmmeta.state, MediaMosaResource.STATE.FULL)


