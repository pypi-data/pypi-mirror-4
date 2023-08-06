# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from mock import patch
from unittest import TestCase
from piston_mini_client import (
    PistonAPI,
    PistonResponseObject,
    returns,
    returns_json,
    returns_list_of,
)
from piston_mini_client.failhandlers import (
    APIError,
    BadRequestError,
    DictFailHandler,
    ExceptionFailHandler,
    ForbiddenError,
    format_response,
    InternalServerErrorError,
    MultiExceptionFailHandler,
    NoneFailHandler,
    NotFoundError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from piston_mini_client.consts import DEBUG_ENVVAR


class GardeningAPI(PistonAPI):
    """Just a dummy API so we can play around with"""
    fail_handler = NoneFailHandler
    default_service_root = 'http://localhost:12345'

    @returns_json
    def grow(self):
        return self._post('/grow', {'plants': 'all'})

    @returns(PistonResponseObject)
    def get_plant(self):
        return self._get('/plant')

    @returns_list_of(PistonResponseObject)
    def get_plants(self):
        return self._get('/plant')


class APIErrorTestCase(TestCase):
    def test_default_repr(self):
        """Check that usually only msg is printed out"""
        err = APIError(msg='foo', body='bar')
        err.debug = False
        self.assertEqual('foo', str(err))

    def test_body_in_verbose_repr(self):
        """Check that body is also included if in verbose mode"""
        err = APIError(msg='foo', body='bar')
        err.debug = True
        self.assertTrue('bar' in str(err))

    def test_data_in_verbose_repr(self):
        """Check that request data is also included if in verbose mode"""
        data = {
            'url': 'foo',
            'method': 'PIDGEON',
            'request_body': 'bla',
            'headers': {'X-SpamLevel': '100'},
        }
        err = APIError(msg='foo', data=data)
        err.debug = True

        output = str(err)
        for key, value in data.items():
            if key == 'headers':
                for k, v in value.items():
                    self.assertTrue("%s: %s" % (k, v) in output)
            else:
                self.assertTrue(value in output)

    def test_response_in_verbose_repr(self):
        data = {
            'url': 'foo',
            'method': 'PIDGEON',
            'request_body': 'bla',
            'headers': {'X-SpamLevel': '100'},
            'response': {'status': 200,
                         'Boo-Yah': 'Waka-waka'},
        }
        body = 'This is my body'
        err = APIError(msg='foo', body=body, data=data)
        err.debug = True

        output = str(err)
        self.assertTrue(
            format_response(data['response'], body) in output)

    @patch('os.environ.get')
    def test_debug_gets_set_from_environment(self, mock_get):
        """Check that debug is initialized from the environment"""
        sentinel = object()
        mock_get.return_value = sentinel

        err = APIError('foo')

        self.assertEqual(err.debug, sentinel)
        mock_get.assert_called_with(DEBUG_ENVVAR, False)


class ExceptionFailHandlerTestCase(TestCase):
    """As this is the default fail handler, we can skip most tests"""
    def test_no_status(self):
        """Check that an exception is raised if no status in response"""
        handler = ExceptionFailHandler('/foo', 'GET', '', {})
        self.assertRaises(APIError, handler.handle, {}, '')

    def test_bad_status_codes(self):
        """Check that APIError is raised if bad status codes are returned"""
        bad_status = ['404', '500', '401']
        handler = ExceptionFailHandler('/foo', 'GET', '', {})
        for status in bad_status:
            self.assertRaises(APIError, handler.handle,
                              {'status': status}, '')


class NoneFailHandlerTestCase(TestCase):
    def test_no_status(self):
        handler = NoneFailHandler('/foo', 'GET', '', {})
        self.assertEqual(None, handler.handle({}, 'not None'))

    def test_bad_status_codes(self):
        """Check that None is returned if bad status codes are returned"""
        bad_status = ['404', '500', '401']
        handler = NoneFailHandler('/foo', 'GET', '', {})
        for status in bad_status:
            self.assertEqual(None, handler.handle({'status': status}, ''))

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_json_on_fail(self, mock_request):
        """Check that NoneFailHandler interacts well with returns_json"""
        mock_request.return_value = {'status': '500'}, 'invalid json'
        api = GardeningAPI()

        self.assertEqual(None, api.grow())

    def test_set_via_class_variable(self):
        """fail_handler can be overridden by specifying it as a class variable.
        """
        api = GardeningAPI()
        self.assertEqual(NoneFailHandler, api.fail_handler)

    def test_forwarding(self):
        """Setting fail_handler on a PistonAPI instance actually works."""
        sentinel = object()
        api = GardeningAPI()
        api.fail_handler = sentinel
        self.assertEqual(sentinel, api.fail_handler)
        # Not a public API, so OK if future changes break this.
        self.assertEqual(sentinel, api._requester._fail_handler)

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_on_fail(self, mock_request):
        """Check that NoneFailHandler interacts well with returns"""
        mock_request.return_value = {'status': '500'}, 'invalid json'
        api = GardeningAPI()

        self.assertEqual(None, api.get_plant())

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_list_of_on_fail(self, mock_request):
        """Check that NoneFailHandler interacts well with returns_list_of"""
        mock_request.return_value = {'status': '500'}, 'invalid json'
        api = GardeningAPI()

        self.assertEqual(None, api.get_plants())

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_json(self, mock_request):
        """Check that NoneFailHandler interacts well with returns_json"""
        mock_request.return_value = {'status': '200'}, '{"foo": "bar"}'
        api = GardeningAPI()

        self.assertEqual({'foo': 'bar'}, api.grow())

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns(self, mock_request):
        """Check that NoneFailHandler interacts well with returns"""
        mock_request.return_value = {'status': '200'}, '{"foo": "bar"}'
        api = GardeningAPI()

        self.assertTrue(isinstance(api.get_plant(), PistonResponseObject))

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_list_of(self, mock_request):
        """Check that NoneFailHandler interacts well with returns_list_of"""
        mock_request.return_value = {'status': '200'}, '[]'
        api = GardeningAPI()

        self.assertEqual([], api.get_plants())


class DictFailHandlerTestCase(TestCase):
    def setUp(self):
        self.response = {'status': '500'}
        self.body = 'invalid json'
        self.expected = {
            'url': '/foo',
            'method': 'GET',
            'request_headers': {},
            'request_body': '',
            'response': self.response,
            'response_body': self.body,
        }
        self.api = GardeningAPI()
        self.api.fail_handler = DictFailHandler

    def test_no_status(self):
        handler = DictFailHandler('/foo', 'GET', '', {})
        del self.response['status']

        self.assertEqual(self.expected, handler.handle({}, self.body))

    def test_bad_status_codes(self):
        bad_status = ['404', '500', '401']
        handler = DictFailHandler('/foo', 'GET', '', {})
        for status in bad_status:
            self.response['status'] = status
            self.assertEqual(self.expected, handler.handle(
                self.expected['response'], self.expected['response_body']))

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_json_on_fail(self, mock_request):
        """Check that DictFailHandler interacts well with returns_json"""
        mock_request.return_value = self.response, self.body
        self.expected['method'] = 'POST'
        self.expected['request_body'] = '{"plants": "all"}'
        self.expected['request_headers'] = {'Content-type': 'application/json'}
        self.expected['url'] = 'http://localhost:12345/grow'

        self.assertEqual(self.expected, self.api.grow())

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_on_fail(self, mock_request):
        """Check that NoneFailHandler interacts well with returns"""
        mock_request.return_value = self.response, self.body
        self.expected['url'] = 'http://localhost:12345/plant'

        self.assertEqual(self.expected, self.api.get_plant())

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_list_of_on_fail(self, mock_request):
        """Check that NoneFailHandler interacts well with returns_list_of"""
        mock_request.return_value = self.response, self.body
        self.expected['url'] = 'http://localhost:12345/plant'

        self.assertEqual(self.expected, self.api.get_plants())

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_json(self, mock_request):
        """Check that NoneFailHandler interacts well with returns_json"""
        mock_request.return_value = {'status': '200'}, '{"foo": "bar"}'

        self.assertEqual({'foo': 'bar'}, self.api.grow())

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns(self, mock_request):
        """Check that NoneFailHandler interacts well with returns"""
        mock_request.return_value = {'status': '200'}, '{"foo": "bar"}'

        self.assertTrue(isinstance(self.api.get_plant(),
                        PistonResponseObject))

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_list_of(self, mock_request):
        """Check that NoneFailHandler interacts well with returns_list_of"""
        mock_request.return_value = {'status': '200'}, '[]'

        self.assertEqual([], self.api.get_plants())


class MultiExceptionFailHandlerTestCase(TestCase):
    def setUp(self):
        self.api = GardeningAPI()
        self.api.fail_handler = MultiExceptionFailHandler

    def test_no_status(self):
        handler = MultiExceptionFailHandler('/foo', 'GET', '', {})

        self.assertRaises(APIError, handler.handle, {}, '')

    def test_bad_status_codes(self):
        bad_status = {
            '400': BadRequestError,
            '401': UnauthorizedError,
            '403': ForbiddenError,
            '404': NotFoundError,
            '500': InternalServerErrorError,
            '503': ServiceUnavailableError,
        }
        handler = MultiExceptionFailHandler('/foo', 'GET', '', {})
        for status, exception in bad_status.items():
            self.assertRaises(exception, handler.handle, {'status': status},
                              '')

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_json_on_fail(self, mock_request):
        """ Check that MultiExceptionFailHandler interacts well with
            returns_json"""
        mock_request.return_value = {'status': '401'}, ''

        self.assertRaises(UnauthorizedError, self.api.grow)

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_on_fail(self, mock_request):
        """Check that MultiExceptionFailHandler interacts well with returns"""
        mock_request.return_value = {'status': '404'}, ''

        self.assertRaises(NotFoundError, self.api.get_plant)

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_list_of_on_fail(self, mock_request):
        """ Check that MultiExceptionFailHandler interacts well with
            returns_list_of"""
        mock_request.return_value = {'status': '500'}, ''

        self.assertRaises(InternalServerErrorError, self.api.get_plants)

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_json(self, mock_request):
        """ Check that MultiExceptionFailHandler interacts well with
            returns_json"""
        mock_request.return_value = {'status': '200'}, '{"foo": "bar"}'

        self.assertEqual({'foo': 'bar'}, self.api.grow())

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns(self, mock_request):
        """Check that MultiExceptionFailHandler interacts well with returns"""
        mock_request.return_value = {'status': '200'}, '{"foo": "bar"}'

        self.assertTrue(isinstance(self.api.get_plant(),
                        PistonResponseObject))

    @patch('httplib2.Http.request')
    def test_interacts_well_with_returns_list_of(self, mock_request):
        """ Check that MultiExceptionFailHandler interacts well with
            returns_list_of"""
        mock_request.return_value = {'status': '200'}, '[]'

        self.assertEqual([], self.api.get_plants())
