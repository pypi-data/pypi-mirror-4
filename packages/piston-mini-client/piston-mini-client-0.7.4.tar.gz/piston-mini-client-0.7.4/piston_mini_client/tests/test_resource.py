# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os
import sys
from mock import patch
from unittest import TestCase
import httplib2
import shutil
import tempfile

from piston_mini_client import (
    APIError,
    PistonAPI, returns_json, returns,
    returns_list_of, PistonResponseObject, PistonSerializable,
    OfflineModeException, safename)
from piston_mini_client.auth import BasicAuthorizer


class PistonAPITestCase(TestCase):
    class CoffeeAPI(PistonAPI):
        default_service_root = 'http://localhost:12345'

        def brew(self):
            self._get('/brew')

    @patch('httplib2.Http.request')
    def test_request(self, mock_request):
        mock_request.return_value = ({'status': '200'}, 'hello world!')
        api = self.CoffeeAPI()
        api._request('/foo', 'POST', body='foo=bar')
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='foo=bar', headers={}, method='POST')

    @patch('httplib2.Http.request')
    def test_request_cached(self, mock_request):
        path = "/foo"
        # setup mock cache
        tmpdir = tempfile.mkdtemp()
        http = httplib2.Http(cache=tmpdir)
        cachekey = self.CoffeeAPI.default_service_root + path
        http.cache.set(
            cachekey, "header\r\n\r\nmy_cached_body\n".encode("utf-8"))
        # ensure that we trigger a error like when offline (no dns)
        mock_request.side_effect = httplib2.ServerNotFoundError("")
        api = self.CoffeeAPI(cachedir=tmpdir, offline_mode=True)
        res = api._request(path, 'GET')
        # check that we get the data we expect
        self.assertEqual(res, "my_cached_body\n")
        # check for nonexisting url
        res = api._request('/bar', 'GET')
        self.assertEqual(res, None)
        # ensure errors on POST, PUT
        self.assertRaises(OfflineModeException, api._request, path, 'POST')
        self.assertRaises(OfflineModeException, api._request, path, 'PUT')
        # cleanup
        shutil.rmtree(tmpdir)

    @patch('httplib2.Http.request')
    def test_request_cached_long_names(self, mock_request):
        # construct a really long path that triggers our safename code
        path = "/foo_with_a_" + 30 * "long_name"
        self.assertTrue(len(path) > 143)
        # setup mock cache
        tmpdir = tempfile.mkdtemp()
        cache = httplib2.FileCache(tmpdir, safe=safename)
        http = httplib2.Http(cache=cache)
        cachekey = self.CoffeeAPI.default_service_root + path
        http.cache.set(
            cachekey.encode('utf-8'),
            "header\r\n\r\nmy_cached_body_from_long_path\n".encode('utf-8'))
        # ensure that we trigger a error like when offline (no dns)
        mock_request.side_effect = httplib2.ServerNotFoundError("")
        api = self.CoffeeAPI(cachedir=tmpdir, offline_mode=True)
        res = api._request(path, 'GET')
        # check that we get the data we expect
        self.assertEqual(res, "my_cached_body_from_long_path\n")
        # cleanup
        shutil.rmtree(tmpdir)

    @patch('httplib2.Http.request')
    def test_auth_request(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI(auth=BasicAuthorizer(username='foo',
                             password='bar'))
        api._request('/fee', 'GET')
        kwargs = mock_request.call_args[1]
        self.assertEqual(kwargs['headers']['Authorization'],
                         'Basic Zm9vOmJhcg==')
        self.assertEqual(kwargs['method'], 'GET')

    @patch('httplib2.Http.request')
    def test_post_no_content_type(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._post('/serve', data={'foo': 'bar'})
        kwargs = mock_request.call_args[1]
        self.assertEqual(kwargs['headers']['Content-type'], 'application/json')
        self.assertEqual(kwargs['method'], 'POST')

    @patch('httplib2.Http.request')
    def test_post_piston_serializable(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')

        class MyCoffeeRequest(PistonSerializable):
            _atts = ('strength',)
        api = self.CoffeeAPI()
        api._post('/serve', data=MyCoffeeRequest(strength='mild'))
        kwargs = mock_request.call_args[1]
        self.assertEqual(kwargs['headers']['Content-type'], 'application/json')
        self.assertEqual(kwargs['method'], 'POST')

    @patch('httplib2.Http.request')
    def test_post_explicit_content_type(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._post('/serve', data={'foo': 'bar'},
                  content_type='application/x-www-form-urlencoded')
        kwargs = mock_request.call_args[1]
        self.assertEqual(kwargs['headers']['Content-type'],
                         'application/x-www-form-urlencoded')
        self.assertEqual(kwargs['method'], 'POST')

    @patch('httplib2.Http.request')
    def test_get_no_args(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._get('/stew')
        args, kwargs = mock_request.call_args
        self.assertTrue(args[0].endswith('/stew'))
        self.assertEqual(kwargs['method'], 'GET')

    @patch('httplib2.Http.request')
    def test_get_with_args(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._get('/stew', args={'foo': 'bar'})
        args, kwargs = mock_request.call_args
        self.assertTrue(args[0].endswith('/stew?foo=bar'))
        self.assertEqual(kwargs['method'], 'GET')

    @patch('httplib2.Http.request')
    def test_valid_status_codes_dont_raise_exception(self, mock_request):
        for status in ['200', '201', '304']:
            response = {'status': status}
            expected_body = '"hello world!"'
            mock_request.return_value = (response, expected_body)
            api = self.CoffeeAPI()
            body = api._get('/simmer')
            self.assertEqual(expected_body, body)
            mock_request.assert_called_with('http://localhost:12345/simmer',
                                            body='', headers={}, method='GET')

    @patch('httplib2.Http.request')
    def test_get_with_extra_args(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._get('/stew?zot=ping', args={'foo': 'bar'})
        args, kwargs = mock_request.call_args
        self.assertTrue(args[0].endswith('/stew?zot=ping&foo=bar'))
        self.assertEqual(kwargs['method'], 'GET')

    def test_path2url_with_no_ending_slash(self):
        resource = PistonAPI('http://example.com/api')
        expected = 'http://example.com/api/frobble'
        self.assertEqual(expected, resource._path2url('frobble'))

    def test_path2url_with_ending_slash(self):
        resource = PistonAPI('http://example.com/api/')
        expected = 'http://example.com/api/frobble'
        self.assertEqual(expected, resource._path2url('frobble'))

    def test_instantiation_fails_with_no_service_root(self):
        try:
            self.CoffeeAPI.default_service_root = None
            self.assertRaises(ValueError, self.CoffeeAPI)
        finally:
            self.CoffeeAPI.default_service_root = 'http://localhost:12345'

    def test_instantiation_fails_with_invalid_scheme(self):
        self.assertRaises(ValueError, self.CoffeeAPI, 'ftp://foobar.baz')

    @patch('httplib2.Http.request')
    def test_request_scheme_switch_to_https(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._request('/foo', 'GET', scheme='https')
        mock_request.assert_called_with('https://localhost:12345/foo',
                                        body='', headers={}, method='GET')

    @patch('httplib2.Http.request')
    def test_get_scheme_switch_to_https(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._get('/foo', scheme='https')
        mock_request.assert_called_with('https://localhost:12345/foo',
                                        body='', headers={}, method='GET')

    @patch('httplib2.Http.request')
    def test_post_scheme_switch_to_https(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._post('/foo', scheme='https')
        mock_request.assert_called_with(
            'https://localhost:12345/foo',
            body='null', headers={'Content-type': 'application/json'},
            method='POST')

    @patch('httplib2.Http.request')
    def test_put_no_data(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._put('/serve')
        kwargs = mock_request.call_args[1]
        self.assertEqual(kwargs['body'], 'null')
        self.assertEqual(kwargs['method'], 'PUT')

    @patch('httplib2.Http.request')
    def test_put_no_content_type(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._put('/serve', data={'foo': 'bar'})
        kwargs = mock_request.call_args[1]
        self.assertEqual(kwargs['headers']['Content-type'], 'application/json')
        self.assertEqual(kwargs['method'], 'PUT')

    @patch('httplib2.Http.request')
    def test_put_piston_serializable(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')

        class MyCoffeeRequest(PistonSerializable):
            _atts = ('strength',)
        api = self.CoffeeAPI()
        api._put('/serve', data=MyCoffeeRequest(strength='mild'))
        kwargs = mock_request.call_args[1]
        self.assertEqual(kwargs['headers']['Content-type'], 'application/json')
        self.assertEqual(kwargs['method'], 'PUT')

    @patch('httplib2.Http.request')
    def test_put_no_scheme(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._put('/serve')
        args, kwargs = mock_request.call_args
        self.assertTrue(args[0].startswith('http://'))
        self.assertEqual(kwargs['method'], 'PUT')

    @patch('httplib2.Http.request')
    def test_put_scheme_switch_to_https(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._put('/foo', scheme='https')
        mock_request.assert_called_with(
            'https://localhost:12345/foo',
            body='null', headers={'Content-type': 'application/json'},
            method='PUT')

    @patch('httplib2.Http.request')
    def test_put(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._put('/serve', data={'foo': 'bar'},
                 content_type='application/x-www-form-urlencoded')
        kwargs = mock_request.call_args[1]
        self.assertEqual(kwargs['body'], 'foo=bar')
        self.assertEqual(kwargs['headers']['Content-type'],
                         'application/x-www-form-urlencoded')
        self.assertEqual(kwargs['method'], 'PUT')

    @patch('httplib2.Http.request')
    def test_customize_headers_on_instance(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api.extra_headers = {'X-Foo': 'bar'}
        api._get('/foo')
        expected_headers = {'X-Foo': 'bar'}
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='', headers=expected_headers, method='GET')
        api._delete('/foo')
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='', headers=expected_headers, method='DELETE')
        expected_headers['Content-type'] = 'application/json'
        api._post('/foo')
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='null', headers=expected_headers, method='POST')
        api._put('/foo')
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='null', headers=expected_headers, method='PUT')

    @patch('httplib2.Http.request')
    def test_customize_headers_on_method_call(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._get('/foo', extra_headers={'X-Foo': 'bar'})
        expected_headers = {'X-Foo': 'bar'}
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='', headers=expected_headers, method='GET')
        api._delete('/foo', extra_headers={'X-Foo': 'bar'})
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='', headers=expected_headers, method='DELETE')
        expected_headers['Content-type'] = 'application/json'
        api._post('/foo', extra_headers={'X-Foo': 'bar'})
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='null', headers=expected_headers, method='POST')
        api._put('/foo', extra_headers={'X-Foo': 'bar'})
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body='null', headers=expected_headers, method='PUT')

    @patch('httplib2.Http.request')
    def test_customize_serializer(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        expected = "serialized!"

        class MySerializer(object):
            def serialize(self, obj):
                return expected

        api = self.CoffeeAPI()
        api.serializers = {'application/json': MySerializer()}
        api._post('/foo', data=[])
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body=expected, headers={'Content-type': 'application/json'},
            method='POST')

        api._put('/foo', data=None)
        mock_request.assert_called_with(
            'http://localhost:12345/foo',
            body=expected, headers={'Content-type': 'application/json'},
            method='PUT')

    @patch('httplib2.Http.request')
    def test_delete_no_scheme(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._delete('/roast')
        args, kwargs = mock_request.call_args
        self.assertTrue(args[0].startswith('http://'))
        self.assertEqual(kwargs['method'], 'DELETE')

    @patch('httplib2.Http.request')
    def test_delete_scheme_switch_to_https(self, mock_request):
        mock_request.return_value = ({'status': '200'}, '""')
        api = self.CoffeeAPI()
        api._delete('/sugar/12', scheme='https')
        mock_request.assert_called_with('https://localhost:12345/sugar/12',
                                        body='', headers={}, method='DELETE')

    def test_cachedir_crash_race_lp803280(self):
        def _simulate_race(path):
            """ this helper simulates the actual race when after
                os.path.exists() a different process creates the dir
            """
            patcher.stop()
            os.makedirs(path)
        # this simulates a race when multiple piston-mini-client helpers
        # try to create the cachedir at the same time (LP: #803280)
        patcher = patch('os.path.exists')
        mock = patcher.start()
        mock.return_value = False
        mock.side_effect = _simulate_race
        tmpdir = os.path.join(tempfile.mkdtemp(), "foo")
        api = self.CoffeeAPI(cachedir=tmpdir)
        self.assertNotEqual(api, None)


class PistonResponseObjectTestCase(TestCase):
    def test_from_response(self):
        obj = PistonResponseObject.from_response('{"foo": "bar"}')
        self.assertEqual('bar', obj.foo)

    def test_from_dict(self):
        obj = PistonResponseObject.from_dict({"foo": "bar"})
        self.assertEqual('bar', obj.foo)


class ReturnsJSONTestCase(TestCase):
    def test_returns_json(self):
        class MyAPI(PistonAPI):
            default_service_root = 'http://foo'

            @returns_json
            def func(self):
                return '{"foo": "bar", "baz": 42}'

        result = MyAPI().func()
        self.assertEqual({"foo": "bar", "baz": 42}, result)

    def test_returns_json_error(self):
        # If the method does not return JSON, we raise a ValueError saying
        # what it did return.
        not_json = 'This cannot be valid JSON'

        class MyAPI(PistonAPI):
            default_service_root = 'http://foo'

            @returns_json
            def its_a_lie(self):
                return not_json

        # If we used unittest2 or testtools, we wouldn't need this.
        try:
            result = MyAPI().its_a_lie()
        except APIError:
            # This is the Python 2 & 3 compatible way of getting an exception.
            exc_type, exc_value, tb = sys.exc_info()
            self.assertEqual(not_json, exc_value.body)
        else:
            self.fail(
                "MyAPI().its_a_lie did not raise. Returned %r instead"
                % (result,))


class ReturnsTestCase(TestCase):
    def test_returns(self):
        class MyAPI(PistonAPI):
            default_service_root = 'http://foo'

            @returns(PistonResponseObject)
            def func(self):
                return '{"foo": "bar", "baz": 42}'

        result = MyAPI().func()
        self.assertTrue(isinstance(result, PistonResponseObject))

    def test_returns_none_allowed(self):
        class MyAPI(PistonAPI):
            default_service_root = 'http://foo'

            @returns(PistonResponseObject, none_allowed=True)
            def func(self):
                return 'null'

        result = MyAPI().func()
        self.assertEqual(result, None)

    def test_returns_none_allowed_normal_response(self):
        class MyAPI(PistonAPI):
            default_service_root = 'http://foo'

            @returns(PistonResponseObject, none_allowed=True)
            def func(self):
                return '{"foo": "bar", "baz": 42}'

        result = MyAPI().func()
        self.assertTrue(isinstance(result, PistonResponseObject))


class ReturnsListOfTestCase(TestCase):
    def test_returns(self):
        class MyAPI(PistonAPI):
            default_service_root = 'http://foo'

            @returns_list_of(PistonResponseObject)
            def func(self):
                return '[{"foo": "bar"}, {"baz": 42}]'

        result = MyAPI().func()
        self.assertEqual(2, len(result))
        self.assertEqual('bar', result[0].foo)
        self.assertEqual(42, result[1].baz)


class PistonSerializableTestCase(TestCase):
    class MySerializable(PistonSerializable):
        _atts = ('foo',)

    def test_init_with_extra_variables(self):
        obj = self.MySerializable(foo='bar', baz=42)
        self.assertEqual('bar', obj.foo)
        self.assertEqual(42, obj.baz)

    def test_init_with_missing_variables(self):
        obj = self.MySerializable()
        self.assertFalse(hasattr(obj, 'foo'))

    def test_missing_required_arguments(self):
        obj = self.MySerializable()
        self.assertRaises(ValueError, obj.as_serializable)

    def test_can_assign_required_arguments_after_init(self):
        obj = self.MySerializable()
        obj.foo = 'bar'
        self.assertEqual({'foo': 'bar'}, obj.as_serializable())

    def test_extra_args_arent_serialized(self):
        obj = self.MySerializable(foo='bar', baz=42)
        self.assertEqual({'foo': 'bar'}, obj.as_serializable())

    def test__as_serializable(self):
        """_as_serializable should still work, although it's deprecated."""
        obj = self.MySerializable(foo='bar')
        self.assertEqual({'foo': 'bar'}, obj._as_serializable())


if __name__ == "__main__":
    import unittest
    unittest.main()
