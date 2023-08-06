# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os
from mock import patch
from tempfile import NamedTemporaryFile
from unittest import TestCase
from piston_mini_client import (
    PistonAPI,
    returns_json,
)
from piston_mini_client.consts import LOG_FILENAME_ENVVAR


class AnnoyAPI(PistonAPI):
    default_service_root = 'http://test.info/api/1.0/'

    @returns_json
    def poke(self, data=None):
        return self._post('/poke/', data=data,
                          extra_headers={'location': 'ribs'})


class LogToFileTestCase(TestCase):
    @patch('httplib2.Http.request')
    def test_requests_are_dumped_to_file(self, mock_request):
        mock_request.return_value = ({'status': '201', 'x-foo': 'bar'},
                                     '"Go away!"')

        with NamedTemporaryFile() as fp:
            api = AnnoyAPI(log_filename=fp.name)

            api.poke([1, 2, 3])

            fp.seek(0)
            data = fp.read()

        lines = data.decode("utf-8").split('\n')
        self.assertEqual(10, len(lines))
        self.assertTrue(lines[0].endswith(
            'Request: POST http://test.info/api/1.0/poke/'))
        self.assertEqual(
            set(['Content-type: application/json',
                 'location: ribs', '', '[1, 2, 3]']),
            set(lines[1:5]))
        self.assertTrue(lines[5].endswith('Response: 201'))
        self.assertEqual(
            set(['x-foo: bar', '', '"Go away!"', '']), set(lines[6:]))

    @patch('httplib2.Http.request')
    def test_invalid_logfile_location_doesnt_fail(self, mock_request):
        mock_request.return_value = ({'status': '201'}, '"Go away!"')
        unlikely_path = 'two/pangolins/walk/into/a/bar/....../so?'
        self.assertFalse(os.path.exists(unlikely_path))
        api = AnnoyAPI(log_filename=unlikely_path)

        response = api.poke()

        self.assertEqual('Go away!', response)

    @patch('httplib2.Http.request')
    def test_perms_issue_doesnt_fail(self, mock_request):
        mock_request.return_value = ({'status': '201'}, '"Go away!"')
        forbidden_path = '/usr/bin/bash'
        self.assertRaises(IOError, open, forbidden_path, 'a')
        api = AnnoyAPI(log_filename=forbidden_path)

        response = api.poke()

        self.assertEqual('Go away!', response)

    @patch('os.environ.get')
    def test_log_filename_is_fetched_from_env(self, mock_get):
        """Check that log_filename is initialized from the environment"""
        sentinel = object()
        mock_get.return_value = sentinel

        api = AnnoyAPI()

        self.assertEqual(api.log_filename, sentinel)
        mock_get.assert_any_call(LOG_FILENAME_ENVVAR)
