# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from mock import patch
from unittest import TestCase
from piston_mini_client import PistonAPI, returns_json
from piston_mini_client.validators import oauth_protected
from piston_mini_client.auth import OAuthAuthorizer, BasicAuthorizer


class BasicAuthorizerTestCase(TestCase):
    def test_sign_request(self):
        auth = BasicAuthorizer(username='foo', password='bar')
        url = 'http://example.com/api'
        headers = {}
        auth.sign_request(url=url, method='GET', body='', headers=headers)
        self.assertTrue('Authorization' in headers)
        self.assertTrue(headers['Authorization'].startswith('Basic '))
        self.assertEqual(headers['Authorization'], 'Basic Zm9vOmJhcg==')

    def test_long_creds_dont_wrap(self):
        auth = BasicAuthorizer(username='foo', password='a' * 500)
        url = 'http://example.com/api'
        headers = {}
        auth.sign_request(url=url, method='GET', body='', headers=headers)
        self.assertTrue('Authorization' in headers)
        self.assertFalse('\n' in headers['Authorization'])


class OAuthAuthorizerTestCase(TestCase):
    def test_sign_request(self):
        auth = OAuthAuthorizer('tkey', 'tsecret', 'ckey', 'csecret')
        url = 'http://example.com/api'
        headers = {}
        auth.sign_request(url=url, method='GET', body='', headers=headers)
        self.assertTrue('Authorization' in headers)
        self.assertTrue(headers['Authorization'].startswith('OAuth '))

    @patch('httplib2.Http.request')
    def test_body_is_signed_if_urlencoded(self, mock_request):
        formencoded = 'application/x-www-form-urlencoded'

        class BathAPI(PistonAPI):
            default_content_type = formencoded
            default_service_root = 'http://example.com'

            @returns_json
            @oauth_protected
            def soak(self):
                return self._post('/soak/', data={'time': 900})

        mock_request.return_value = {'status': '200'}, '"done"'

        auth = OAuthAuthorizer('tkey', 'tsecret', 'ckey', 'csecret')
        api = BathAPI(auth=auth)

        response = api.soak()

        self.assertEqual('done', response)
        self.assertEqual(1, mock_request.call_count)
        args, kwargs = mock_request.call_args
        self.assertEqual(formencoded, kwargs['headers']['Content-Type'])
        auth_header = kwargs['headers']['Authorization']
        self.assertTrue(auth_header.startswith('OAuth '))

    @patch('httplib2.Http.request')
    def test_post_works_with_no_body(self, mock_request):
        cases = [
            'application/x-www-form-urlencoded',
            'application/json',
        ]

        class ShowerAPI(PistonAPI):
            default_service_root = 'http://example.com'

            @returns_json
            @oauth_protected
            def soak(self):
                return self._post('/noop/', data='')
        auth = OAuthAuthorizer('tkey', 'tsecret', 'ckey', 'csecret')
        for content_type in cases:
            mock_request.return_value = {'status': '200'}, '"done"'
            api = ShowerAPI(auth=auth)
            api.default_content_type = content_type

            response = api.soak()

            self.assertEqual('done', response)
            args, kwargs = mock_request.call_args
            self.assertEqual(content_type, kwargs['headers']['Content-Type'])
            auth_header = kwargs['headers']['Authorization']
            self.assertTrue(auth_header.startswith('OAuth '))
