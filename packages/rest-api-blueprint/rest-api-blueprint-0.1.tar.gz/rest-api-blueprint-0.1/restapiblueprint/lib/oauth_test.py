import mock
import unittest
import urlparse

from restapiblueprint.lib import oauth

# Test consumer key and secret.
KEY = 'akey'
SECRET = 'asecret'


def _test_get_secret(key):
    if key == KEY:
        return SECRET
    raise KeyError(key)


class TestOauthUtils(unittest.TestCase):

    def test_get_HMAC_SHA1_signature_as_url(self):
        url = oauth.get_HMAC_SHA1_signature_as_url(
            KEY, SECRET, 'http://a.b.c', 'GET')
        self.assertEqual(oauth.verify(_test_get_secret, url, 'GET', {}), KEY)

    def test_get_HMAC_SHA1_signature_as_url_fail(self):
        url = oauth.get_HMAC_SHA1_signature_as_url(
            KEY, SECRET, 'http://a.b.c', 'GET')
        self.assertEqual(
            oauth.verify(_test_get_secret, url, 'POST', {}), None)

    def test_get_HMAC_SHA1_signature_as_url_with_query(self):
        url = oauth.get_HMAC_SHA1_signature_as_url(
            KEY, SECRET, 'http://a.b.c?name=tim', 'GET')
        self.assertEqual(oauth.verify(_test_get_secret, url, 'GET', {}), KEY)

    def test_get_HMAC_SHA1_signature_as_header(self):
        url = 'http://a.b.c'
        header = oauth.get_HMAC_SHA1_signature_as_header(
            KEY, SECRET, url, 'GET')
        self.assertEqual(
            oauth.verify(_test_get_secret, url, 'GET', header), KEY)

    def test_get_HMAC_SHA1_signature_as_header_fail(self):
        url = 'http://a.b.c'
        header = oauth.get_HMAC_SHA1_signature_as_header(
            KEY, SECRET, url, 'GET')
        self.assertEqual(
            oauth.verify(_test_get_secret, 'http://x.y.z', 'GET', header), None)

    def test_get_HMAC_SHA1_signature_as_header_with_query(self):
        url = 'http://a.b.c?name=tim'
        header = oauth.get_HMAC_SHA1_signature_as_header(
            KEY, SECRET, url, 'GET')
        self.assertEqual(
            oauth.verify(_test_get_secret, url, 'GET', header), KEY)

    def test_against_google_example(self):
        # Confirm that we create the same signature as provided in Appendix A of
        # http://oauth.googlecode.com/svn/spec/ext/consumer_request/
        #     1.0/drafts/2/spec.html

        def my_time():
            return 1191242096

        def my_nonce():
            return 'kllo9940pd9333jh'

        key = 'dpf43f3p2l4k3l03'
        secret = 'kd94hf93k423kf44'

        with mock.patch('time.time', my_time):
            with mock.patch('oauth2.generate_nonce', my_nonce):
                url = oauth.get_HMAC_SHA1_signature_as_url(
                    key, secret, 'http://provider.example.net/profile', 'GET')

        query_string = urlparse.urlparse(url).query
        self.assertEqual(
            urlparse.parse_qs(query_string)['oauth_signature'][0],
            u'IxyYZfG2BaKh8JyEGuHCOin/4bA=')
