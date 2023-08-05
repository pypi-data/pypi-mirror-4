import unittest
import logging
import mock
import requests
import backplane as bp

logging.disable(logging.CRITICAL)

class TestErrors(unittest.TestCase):

    msg = 'Some error message'

    def test_bp_call_err(self):
        try:
            raise bp.BackplaneCallError, self.msg
        except bp.BackplaneCallError, e:
            self.assertEqual(e.description, self.msg)
            self.assertEqual(str(e), 'backplane call failed: ' + self.msg)

    def test_bp_err(self):
        try:
            raise bp.BackplaneError, self.msg
        except bp.BackplaneError, e:
            self.assertEqual(e.response, self.msg)
            self.assertEqual(str(e), self.msg)

    def test_unauthorized_scope_err(self):
        try:
            raise bp.UnauthorizedScopeError, self.msg
        except bp.UnauthorizedScopeError, e:
            self.assertEqual(e.response, self.msg)
            self.assertEquals(str(e), self.msg)

    def test_expired_token_err(self):
        try:
            raise bp.ExpiredTokenError, self.msg
        except bp.ExpiredTokenError, e:
            self.assertEqual(e.response, self.msg)
            self.assertEquals(str(e), self.msg)

    def test_invalid_token_err(self):
        try:
            raise bp.InvalidTokenError, self.msg
        except bp.InvalidTokenError, e:
            self.assertEqual(e.response, self.msg)
            self.assertEquals(str(e), self.msg)


class TestClassInits(unittest.TestCase):

    def test_token(self):
        t = bp.Token('token', 'type', 'refresh', 'expires', 'scope')
        self.assertEquals(t.access_token, 'token')
        self.assertEquals(t.type, 'type')
        self.assertEquals(t.refresh_token, 'refresh')
        self.assertEquals(t.expires_in, 'expires')
        self.assertEquals(t.scope, 'scope')

    def test_message(self):
        m = bp.Message('bus', 'channel', 'type', 'payload', 'sticky',
                       'url', 'source', 'expire')
        self.assertEquals(m.bus, 'bus')
        self.assertEquals(m.channel, 'channel')
        self.assertEquals(m.type, 'type')
        self.assertEquals(m.payload, 'payload')
        self.assertEquals(m.sticky, 'sticky')
        self.assertEquals(m.messageURL, 'url')
        self.assertEquals(m.source, 'source')
        self.assertEquals(m.expire, 'expire')

    def test_wrapper(self):
        w = bp.Wrapper('next', 'messages', 'more')
        self.assertEquals(w.next_url, 'next')
        self.assertEquals(w.messages, 'messages')
        self.assertEquals(w.more, 'more')

    def test_client_creds(self):
        c = bp.ClientCredentials('url', 'id', 'secret', 'token')
        self.assertEquals(c.server_url, 'url')
        self.assertEquals(c.client_id, 'id')
        self.assertEquals(c.client_secret, 'secret')
        self.assertEquals(c.token, 'token')

class MockHttpResponse(object):
    def __init__(self, data, status_code):
        self.data_ = data
        self.status_code_ = status_code
    @property
    def text(self):
        return self.data_
    @property
    def status_code(self):
        return self.status_code_

class TestClient(unittest.TestCase):

    creds = bp.ClientCredentials('url', 'id', 'secret')
    token = bp.Token('AAblVpGm8g4llDLdqnM4y0',
                     'Bearer',
                     'ARpIAYznoB4QenmLQIkbgH',
                     604799,
                     'bus:bus1 channel:I5sRIdzNdDxwcKnPPDB10oB1hwMfJYUb')

    def tearDown(self):
        self.creds.token = None

    def add_token_to_creds(self):
        self.creds.token = self.token

    def get_client(self, initialize=False):
        return bp.Client(self.creds, initialize=initialize)

    # Scope should be passed when initializing only
    def test_init_req_when_scope(self):
        self.assertRaises(AssertionError, bp.Client, self.creds, False, 'scope')

    @mock.patch('requests.get')
    def test_get_regular_token(self, mockHttpRequest):
        # Test with successful response
        body = 'f({"token_type":"Bearer","access_token":"AAblVpGm8g4llDLdqnM4y0","expires_in":604799,"scope":"bus:bus1 channel:I5sRIdzNdDxwcKnPPDB10oB1hwMfJYUb","refresh_token":"ARpIAYznoB4QenmLQIkbgH"});'
        mockHttpRequest.side_effect = [MockHttpResponse(body, 200)]
        client = self.get_client()
        t = client.get_regular_token('bus')
        self.assertTrue(isinstance(t, bp.Token))
        self.assertEquals(t.type, 'Bearer')
        self.assertEquals(t.access_token, 'AAblVpGm8g4llDLdqnM4y0')
        self.assertEquals(t.expires_in, 604799)
        self.assertEquals(
            t.scope, 'bus:bus1 channel:I5sRIdzNdDxwcKnPPDB10oB1hwMfJYUb')
        self.assertEquals(t.refresh_token, 'ARpIAYznoB4QenmLQIkbgH')

        # Test with error response
        body = 'f({"error":"invalid_request","error_description":"Invalid bus: invalid_bus"});'
        # Since the API returns JSONP, status is 200 even on errors
        mockHttpRequest.side_effect = [MockHttpResponse(body, 200)]
        self.assertRaises(
            bp.BackplaneError, client.get_regular_token, 'bus')

    @mock.patch('requests.post')
    def test_get_token(self, mockHttpRequest):
        # Test with successful response
        body = '{"token_type":"Bearer","access_token":"PCxNCDPos1kmsiTAZ7U08v","expires_in":31535999,"scope":"bus:bus2","refresh_token":"PRLX8EZdc1tI1E4nSvAGky"}'
        mockHttpRequest.side_effect = [MockHttpResponse(body, 200)]
        client = self.get_client()
        t = client.get_token('bus')
        self.assertTrue(isinstance(t, bp.Token))
        self.assertEquals(t.type, 'Bearer')
        self.assertEquals(t.access_token, 'PCxNCDPos1kmsiTAZ7U08v')
        self.assertEquals(t.expires_in, 31535999)
        self.assertEquals(t.scope, 'bus:bus2')
        self.assertEquals(t.refresh_token, 'PRLX8EZdc1tI1E4nSvAGky')

        # Test with error response
        body = '{"error":"invalid_scope","error_description":"unauthorized scope: bus:bus1"}'
        mockHttpRequest.side_effect = [MockHttpResponse(body, 400)]
        self.assertRaises(
            bp.UnauthorizedScopeError, client.get_token, 'bus')

    @mock.patch('requests.post')
    def test_refresh_token(self, mockHttpRequest):
        # Test with successful response
        #
        # This is to init client credentials with a token
        body1 = '{"token_type":"Bearer","access_token":"PCACxAt8DEambDcO6pGTIx","expires_in":31535999,"scope":"bus:bus1","refresh_token":"PR6fxIkJLHbgZiE7w3B2ZM"}'
        # This is to refresh the token
        body2 = '{"token_type":"Bearer","access_token":"PC3Rm17rJUM3jmbtB34JEJ","expires_in":31535999,"scope":"bus:bus2","refresh_token":"PR5LoqnbxvF93SOGWqGnrs"}'
        mockHttpRequest.side_effect = [
            MockHttpResponse(body1, 200),
            MockHttpResponse(body2, 200)]
        client = self.get_client(True)
        client.refresh_token()
        t = client.credentials.token
        self.assertTrue(isinstance(t, bp.Token))
        self.assertEquals(t.type, 'Bearer')
        self.assertEquals(t.access_token, 'PC3Rm17rJUM3jmbtB34JEJ')
        self.assertEquals(t.expires_in, 31535999)
        self.assertEquals(t.scope, 'bus:bus2')
        self.assertEquals(t.refresh_token, 'PR5LoqnbxvF93SOGWqGnrs')

        # Test with error response
        body = '{"error":"invalid_request","error_description":"invalid token"}'
        mockHttpRequest.side_effect = [MockHttpResponse(body, 403)]
        self.assertRaises(
            bp.InvalidTokenError, client.refresh_token)

    @mock.patch('requests.post')
    def test_post_message(self, mockHttpRequest):
        msg = bp.Message('bus', 'channel', 'type', {'hehe': 'haha'}, True)

        # Test with successful response
        mockHttpRequest.side_effect = [MockHttpResponse(None, 201)]
        self.add_token_to_creds()
        client = self.get_client()
        client.post_message(msg)

        # Test with error response
        body = '{"error":"Invalid bus - channel binding "}'
        mockHttpRequest.side_effect = [MockHttpResponse(body, 403)]
        self.assertRaises(bp.BackplaneError, client.post_message, msg)

    @mock.patch('requests.get')
    def test_get_single_message(self, mockHttpRequest):
        body = '{"messageURL":"https://url/v2/message/mid","source":"http://localhost","type":"identity/login","bus":"bus1","channel":"asxLPUhCFd7u7RLwJLAeoLm2DOeMbSdM","sticky":"true","expire":"2012-11-10T08:07:11Z","payload":{"hehe":"haha"}}'
        mockHttpRequest.side_effect = [MockHttpResponse(body, 200)]
        self.add_token_to_creds()
        client = self.get_client()
        m = client.get_single_message('mid')
        self.assertEquals(m.bus, 'bus1')
        self.assertEquals(m.expire, '2012-11-10T08:07:11Z')
        # The method should have constructed URL from a message ID
        self.assertTrue('/v2/message/mid' in str(mockHttpRequest.mock_calls))

    @mock.patch('requests.get')
    def test_get_messages(self, mockHttpRequest):
        body1 = '{"nextURL":"https://localhost/v2/messages?since=2012-11-10T01:30:28.037Z-CPbqzW16zA","messages":[{"messageURL":"https://localhost/v2/message/2012-11-10T00:07:11.512Z-dnveTh0M86","source":"http://localhost","type":"identity/login","bus":"bus1","channel":"asxLPUhCFd7u7RLwJLAeoLm2DOeMbSdM","sticky":"true","expire":"2012-11-10T08:07:11Z","payload":{"hehe":"haha"}},{"messageURL":"https://localhost/v2/message/2012-11-10T00:26:57.184Z-vQeFesXKud","source":"http://localhost","type":"identity/login","bus":"bus1","channel":"20Vh6Iwar7FNwH8v3AyXZUehQKaU22Bu","sticky":"true","expire":"2012-11-10T08:26:57Z","payload":{"context":"http://thinkwork/backplane2/token.html","identities":{"startIndex":0,"itemsPerPage":1,"totalResults":1,"entry":[{"id":"http://twitter.com/account/profile?user_id=144800941","displayName":"disp","photos":[{"type":"other","value":"http://a0.twimg.com/profile_images/1.jpg"}],"accountUri":"http://twitter.com/account/profile?user_id=14448848322","domain":"twitter.com","name":{"formatted":"disp"},"preferredUsername":"pref","urls":[{"type":"profile","value":"http://twitter.com/pref"}],"accessCredentials":{"access_credential_type":"oauth1","oauth_token":"1rrBrimru","oauth_token_secret":"JmUdxKoi"},"engage":{"following":["http://twitter.com/account/profile?user_id=172264980","http://twitter.com/account/profile?user_id=167336804","http://twitter.com/account/profile?user_id=145843434"],"followers":["http://twitter.com/account/profile?user_id=85736","http://twitter.com/account/profile?user_id=9857376","http://twitter.com/account/profile?user_id=433474458"],"friendships":["http://twitter.com/account/profile?user_id=172264980","http://twitter.com/account/profile?user_id=1475934"],"url":"http://twitter.com/pref","photo":"http://a0.twimg.com/profile_images/1","identifier":"http://twitter.com/account/profile?user_id=4598569","providerName":"Twitter"}}]}}},{"messageURL":"https://localhost/v2/message/2012-11-10T01:30:28.037Z-CPbqzW16zA","source":"http://localhost","type":"identity/login","bus":"bus1","channel":"asxLPUhCFd7u7RLwJLAeoLm2DOeMbSdM","sticky":"true","expire":"2012-11-10T09:30:28Z","payload":{"hehe":"haha"}}],"moreMessages":false}'
        body2 = '{"nextURL":"https://localhost/v2/messages?since=2012-11-10T01:30:28.037Z-CPbqzW16zA","messages":[],"moreMessages":false}'
        mockHttpRequest.side_effect = [
            MockHttpResponse(body1, 200),
            MockHttpResponse(body2, 200)]
        self.add_token_to_creds()
        client = self.get_client()
        w = client.get_messages()
        self.assertEquals(
            w.messages[1].payload['identities']['entry'][0]['displayName'],
            'disp')
        w = client.get_messages(w)
        self.assertEquals(w.more, False)

class TestFunctions(unittest.TestCase):

    @mock.patch('requests.get')
    def test_call_backplane(self, mockHttpRequest):
        body = 'Not found'
        mockHttpRequest.side_effect = (
            lambda *args, **kwargs: MockHttpResponse(body, 404))
        self.assertRaises(
            bp.BackplaneError, bp._call_backplane, 'url', 'GET')
        try:
            bp._call_backplane('url', 'GET')
        except bp.BackplaneError, e:
            self.assertEqual(e.response, body)
            self.assertEqual(str(e), body)

        def raise_hell(*args):
            raise Exception('bogus error')
        mockHttpRequest.side_effect = raise_hell
        self.assertRaises(bp.BackplaneCallError, bp._call_backplane, 'u', 'GET')


if __name__ == "__main__":
    unittest.main()
