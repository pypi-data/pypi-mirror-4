import unittest

from minimock import mock, TraceTracker, Mock
import requests

from mediamosa.api import MediaMosaAPI, ApiException


class TestLoginFunctions(unittest.TestCase):

    def setUp(self):
        self.url = 'http://video.example.com'
        self.username = 'test_username'
        self.app_id = 5
        self.secret = 'test_secret'

        # mock requests library
        self.tt = TraceTracker()
        self.api = MediaMosaAPI(self.url)
        mock('self.api.session', tracker=self.tt)

        self.response = Mock('requests.Response')
        self.response.status_code = 200
        self.api.session.get.mock_returns = self.response
        self.api.session.post.mock_returns = self.response

    def test_get_absolute_rui(self):
        uri = '/a/relative/url'
        self.assertEquals(self.api._get_absolute_uri(uri), self.url + uri)

    def test_internal_get_call(self):
        # setup
        uri = '/login'
        self.response.content = open(
            'tests/data/login_challenge_response.xml').read()
        # test
        self.api._get(uri)
        # validate
        self.assertTrue(
            self.tt.check("Called "
                + "self.api.session.get('http://video.example.com/login', params={})"))

    def test_internal_post_call(self):
        # setup
        uri = '/login'
        self.response.content = open(
            'tests/data/login_challenge_response.xml').read()
        # test
        self.api._post(uri)
        # validate
        self.assertTrue(
            self.tt.check("Called "
                + "self.api.session.post('http://video.example.com/login', data={})"))

    def test_login_get_challenge(self):
        # setup
        self.api.username = self.username
        self.response.content = open(
            'tests/data/login_challenge_response.xml').read()
        # test
        challenge = self.api._login_challenge()
        # validate
        self.assertEquals(challenge, "92dc06bbb703f14354fdfbede9b62ff9")

    def test_login_get_failed_challenge(self):
        # setup
        self.api.username = self.username
        self.response.content = open(
            'tests/data/login_challenge_invalid_account_response.xml').read()
        # validate
        self.assertRaises(ApiException, self.api._login_challenge)

    def test_login_send_challenge_response(self):
        # setup
        self.api.username = self.username
        self.api.secret = self.secret
        self.response.content = open(
            'tests/data/login_challenge_response_response.xml').read()
        # test
        success = self.api._login_response("92dc06bbb703f14354fdfbede9b62ff9")
        # validate
        self.assertEquals(success, True)

    def test_login_send_challenge_failed_response(self):
        # setup
        self.api.username = self.username
        self.api.secret = self.secret
        self.response.content = open(
            'tests/data/login_invalid_challenge_response_response.xml').read()
        # test
        success = self.api._login_response("92dc06bbb703f14354fdfbede9b62ff9")
        # validate
        self.assertEquals(success, False)

    def test_successful_authentication(self):
        # setup
        mock('self.api._login_challenge', returns='xxx', tracker=self.tt)
        mock('self.api._login_response', returns=True, tracker=self.tt)
        # test
        success = self.api.authenticate(self.username, self.secret)
        # validate
        self.assertEquals(success, True)

    def test_failed_authentication(self):
        # setup
        mock('self.api._login_challenge', returns='xxx', tracker=self.tt)
        mock('self.api._login_response', returns=False, tracker=self.tt)
        # test
        success = self.api.authenticate(self.username, self.secret)
        # validate
        self.assertEquals(success, False)
