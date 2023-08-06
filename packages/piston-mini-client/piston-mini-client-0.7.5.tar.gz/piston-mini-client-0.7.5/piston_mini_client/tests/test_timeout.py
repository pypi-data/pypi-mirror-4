# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import socket
from unittest import TestCase
from mock import patch
from piston_mini_client import PistonAPI
from piston_mini_client.failhandlers import APIError


class LazyAPI(PistonAPI):
    default_service_root = 'http://test.info/api/1.0/'
    default_timeout = 42

    def sleep(self, amount):
        return self._get('/snooze/%s/' % amount)


class TimeoutTestCase(TestCase):
    @patch('os.environ.get')
    @patch('httplib2.Http')
    def test_timeout_in_constructor_wins(self, mock_http, mock_get):
        mock_get.return_value = '3.14'
        api = LazyAPI(timeout=1)
        self.assertEqual(1, api._timeout)
        mock_http.assert_called_with(cache=None, proxy_info=None, timeout=1,
                                     disable_ssl_certificate_validation=True)

    @patch('os.environ.get')
    @patch('httplib2.Http')
    def test_timeout_in_env_beats_class_default(self, mock_http, mock_get):
        mock_get.return_value = '3.14'
        api = LazyAPI()
        self.assertEqual(3.14, api._timeout)
        mock_http.assert_called_with(cache=None, proxy_info=None, timeout=3.14,
                                     disable_ssl_certificate_validation=True)

    @patch('os.environ.get')
    @patch('httplib2.Http')
    def test_no_envvar_falls_back_to_class_default(self, mock_http, mock_get):
        mock_get.return_value = None
        api = LazyAPI()
        self.assertEqual(42, api._timeout)
        mock_http.assert_called_with(cache=None, proxy_info=None, timeout=42)

    @patch('os.environ.get')
    @patch('httplib2.Http')
    def test_no_nothing_falls_back_to_system_default(self, mock_http,
                                                     mock_get):
        class DefaultAPI(PistonAPI):
            default_service_root = 'http://test.info/api/1.0/'

        mock_get.return_value = None
        api = DefaultAPI()
        self.assertEqual(None, api._timeout)
        mock_http.assert_called_with(cache=None, proxy_info=None, timeout=None)

    @patch('os.environ.get')
    @patch('httplib2.Http')
    def test_invalid_envvar_uses_class_default(self, mock_http, mock_get):
        mock_get.return_value = 'invalid'
        api = LazyAPI()
        self.assertEqual(42, api._timeout)
        mock_http.assert_called_with(cache=None, proxy_info=None, timeout=42,
                                     disable_ssl_certificate_validation=True)

    @patch('httplib2.HTTPConnectionWithTimeout.connect')
    def test_timeout_is_handled_by_failhandler(self, mock_connect):
        mock_connect.side_effect = socket.timeout
        api = LazyAPI()

        self.assertRaises(APIError, api.sleep, 2)
