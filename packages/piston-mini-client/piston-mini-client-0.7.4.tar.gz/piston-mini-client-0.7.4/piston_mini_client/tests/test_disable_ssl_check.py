# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os

from mock import patch
from unittest import TestCase

from piston_mini_client import PistonAPI
from piston_mini_client.consts import DISABLE_SSL_VALIDATION_ENVVAR


class DentistAPI(PistonAPI):
    default_service_root = 'http://localhost:12345'

    def appointments(self):
        self._get('/appointments')


class DisableSSLVerificationTestCase(TestCase):
    def setUp(self):
        if DISABLE_SSL_VALIDATION_ENVVAR in os.environ:
            self.orig_disable_ssl = os.environ[DISABLE_SSL_VALIDATION_ENVVAR]
            del os.environ[DISABLE_SSL_VALIDATION_ENVVAR]

    def tearDown(self):
        if DISABLE_SSL_VALIDATION_ENVVAR in os.environ:
            del os.environ[DISABLE_SSL_VALIDATION_ENVVAR]
        if hasattr(self, 'orig_disable_ssl'):
            os.environ[DISABLE_SSL_VALIDATION_ENVVAR] = self.orig_disable_ssl

    @patch('httplib2.Http')
    def test_dont_disable(self, mock_http):
        api = DentistAPI()

        self.assertTrue('disable_ssl_certificate_validation' not in
                        mock_http.call_args[1])

    @patch('httplib2.Http')
    def test_disable_via_constructor(self, mock_http):
        api = DentistAPI(disable_ssl_validation=True)

        self.assertTrue('disable_ssl_certificate_validation' in
                        mock_http.call_args[1])

    @patch('httplib2.Http')
    def test_disable_via_envvar(self, mock_http):
        os.environ[DISABLE_SSL_VALIDATION_ENVVAR] = '1'
        api = DentistAPI()

        self.assertTrue('disable_ssl_certificate_validation' in
                        mock_http.call_args[1])
