# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os

from unittest import TestCase

from piston_mini_client import PistonAPI


class DentistAPI(PistonAPI):
    default_service_root = 'http://localhost:12345'

    def appointments(self):
        self._get('/appointments')


class ProxySupportTestCase(TestCase):

    def setUp(self):
        for envvar in ("http_proxy", "https_proxy"):
            if envvar in os.environ:
                del os.environ[envvar]

    def test_basic_proxy(self):
        os.environ["http_proxy"] = "http://localhost:3128"
        api = DentistAPI()
        proxy_info = api._http["http"].proxy_info
        self.assertNotEqual(proxy_info, None)
        self.assertEqual(proxy_info.proxy_host, "localhost")
        self.assertEqual(proxy_info.proxy_port, 3128)

    def test_basic_https_proxy(self):
        # not the https this time
        os.environ["https_proxy"] = "https://localhost:3128"
        api = DentistAPI(service_root="https://localhost:12345")
        proxy_info = api._http["https"].proxy_info
        self.assertNotEqual(proxy_info, None)
        self.assertEqual(proxy_info.proxy_host, "localhost")
        self.assertEqual(proxy_info.proxy_port, 3128)

    def test_auth_proxy(self):
        os.environ["http_proxy"] = "http://user:pass@localhost:3128"
        api = DentistAPI()
        proxy_info = api._http["http"].proxy_info
        self.assertNotEqual(proxy_info, None)
        self.assertEqual(proxy_info.proxy_host, "localhost")
        self.assertEqual(proxy_info.proxy_port, 3128)
        self.assertEqual(proxy_info.proxy_user, "user")
        self.assertEqual(proxy_info.proxy_pass, "pass")

    def test_no_proxy(self):
        api = DentistAPI()
        proxy_info = api._http["http"].proxy_info
        self.assertEqual(proxy_info, None)

    def test_httplib2_proxy_type_http_no_tunnel(self):
        # test that patching httplib2 with our own socks.py works
        import httplib2
        import piston_mini_client
        self.assertEqual(piston_mini_client.socks.PROXY_TYPE_HTTP_NO_TUNNEL,
                         httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL)

if __name__ == "__main__":
    import unittest
    unittest.main()
