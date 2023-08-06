# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from piston_mini_client.validators import (
    basic_protected,
    oauth_protected,
    validate,
    validate_integer,
    validate_pattern,
    ValidationException,
)
from piston_mini_client.auth import OAuthAuthorizer, BasicAuthorizer
from unittest import TestCase


class ValidatePatternTestCase(TestCase):
    def setUp(self):
        self.called = False

    def test_raises_if_arg_omitted(self):
        @validate_pattern('arg', 'foo')
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func)
        self.assertFalse(self.called)

    def test_raises_if_arg_not_named(self):
        @validate_pattern('arg', 'foo')
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, 'foo')
        self.assertFalse(self.called)

    def test_raises_if_arg_not_a_string(self):
        @validate_pattern('arg', r'\d+')
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, arg=42)
        self.assertFalse(self.called)

    def test_raises_if_arg_doesnt_match(self):
        @validate_pattern('arg', 'foo')
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, 'bar')
        self.assertFalse(self.called)

    def test_match_must_be_complete(self):
        @validate_pattern('arg', 'foo')
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, arg='foobar')
        self.assertFalse(self.called)

    def test_match_success(self):
        @validate_pattern('arg', '\w{4,7}')
        def func(arg):
            self.called = True
        func(arg='foobar')
        self.assertTrue(self.called)

    def test_optional_can_be_omitted(self):
        @validate_pattern('arg', 'foo', required=False)
        def func(arg=None):
            self.called = True
        func()
        self.assertTrue(self.called)

    def test_optional_must_match_if_provided(self):
        @validate_pattern('arg', 'foo', required=False)
        def func(arg=None):
            self.called = True
        self.assertRaises(ValidationException, func, arg='bar')
        self.assertFalse(self.called)


class ValidateIntegerTestCase(TestCase):
    def setUp(self):
        self.called = False

    def test_raises_if_arg_omitted(self):
        @validate_integer('arg')
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func)
        self.assertFalse(self.called)

    def test_raises_if_arg_not_named(self):
        @validate_integer('arg')
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, 42)
        self.assertFalse(self.called)

    def test_raises_if_arg_not_an_int(self):
        @validate_integer('arg')
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, arg='foo')
        self.assertRaises(ValidationException, func, arg=7.5)
        self.assertFalse(self.called)

    def test_raises_if_arg_below_min(self):
        @validate_integer('arg', min=4)
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, arg=2)
        self.assertFalse(self.called)

    def test_raises_if_arg_above_max(self):
        @validate_integer('arg', max=4)
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, arg=6)
        self.assertFalse(self.called)

    def test_optional_can_be_omitted(self):
        @validate_integer('arg', required=False)
        def func(arg=None):
            self.called = True
        func()
        self.assertTrue(self.called)

    def test_optional_must_validate_if_provided(self):
        @validate_integer('arg', required=False)
        def func(arg=None):
            self.called = True
        self.assertRaises(ValidationException, func, arg='bar')
        self.assertFalse(self.called)

    def test_validate_success(self):
        @validate_integer('arg', min=4, max=10)
        def func(arg):
            self.called = True
        func(arg=7)
        self.assertTrue(self.called)


class ValidateTestCase(TestCase):
    class SomeClass(object):
        pass

    def setUp(self):
        self.called = False

    def test_raises_if_arg_omitted(self):
        @validate('arg', self.SomeClass)
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func)
        self.assertFalse(self.called)

    def test_raises_if_arg_not_named(self):
        @validate('arg', self.SomeClass)
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, True)
        self.assertFalse(self.called)

    def test_raises_if_arg_not_isinstance(self):
        @validate('arg', self.SomeClass)
        def func(arg):
            self.called = True
        self.assertRaises(ValidationException, func, arg='foo')
        self.assertRaises(ValidationException, func, arg=7.5)
        self.assertRaises(ValidationException, func, arg=1)
        self.assertFalse(self.called)

    def test_optional_can_be_omitted(self):
        @validate('arg', self.SomeClass, required=False)
        def func(arg=None):
            self.called = True
        func()
        self.assertTrue(self.called)

    def test_optional_must_validate_if_provided(self):
        @validate('arg', self.SomeClass, required=False)
        def func(arg=None):
            self.called = True
        self.assertRaises(ValidationException, func, arg='bar')
        self.assertFalse(self.called)

    def test_validate_success(self):
        @validate('arg', self.SomeClass)
        def func(arg):
            self.called = True
        func(arg=self.SomeClass())
        self.assertTrue(self.called)


class OAuthProtectedTestCase(TestCase):
    """ The oauth_protected decorator can only be applied to methods
        (or functions that receive a first 'self' arg), as it
        needs to check for the self._auth attribute.
        So we define a small class for each test to use here.
    """
    class MyAPI(object):
        called = False

        @oauth_protected
        def method(self):
            self.called = True

    def test_fail_if_no_auth(self):
        api = self.MyAPI()
        self.assertRaises(ValidationException, api.method)
        self.assertFalse(api.called)

    def test_fail_if_auth_is_none(self):
        api = self.MyAPI()
        api._auth = None
        self.assertRaises(ValidationException, api.method)
        self.assertFalse(api.called)

    def test_fail_if_auth_isnt_oauth(self):
        api = self.MyAPI()
        api._auth = BasicAuthorizer('username', 'password')
        self.assertRaises(ValidationException, api.method)
        self.assertFalse(api.called)

    def test_success(self):
        auth = OAuthAuthorizer('tkey', 'tsecret', 'ckey', 'csecret')
        api = self.MyAPI()
        api._auth = auth
        api.method()
        self.assertTrue(api.called)

    def test_success_with_subclass(self):
        class MyOAuth(OAuthAuthorizer):
            pass
        auth = MyOAuth('tkey', 'tsecret', 'ckey', 'csecret')
        api = self.MyAPI()
        api._auth = auth
        api.method()
        self.assertTrue(api.called)


class BasicProtectedTestCase(TestCase):
    """ The basic_protected decorator can only be applied to methods
        (or functions that receive a first 'self' arg), as it
        needs to check for the self._auth attribute.
        So we define a small class for each test to use here.
    """
    class MyAPI(object):
        called = False

        @basic_protected
        def method(self):
            self.called = True

    def test_fail_if_no_auth(self):
        api = self.MyAPI()
        self.assertRaises(ValidationException, api.method)
        self.assertFalse(api.called)

    def test_fail_if_auth_is_none(self):
        api = self.MyAPI()
        api._auth = None
        self.assertRaises(ValidationException, api.method)
        self.assertFalse(api.called)

    def test_fail_if_auth_isnt_basic(self):
        api = self.MyAPI()
        api._auth = OAuthAuthorizer('tkey', 'tsecret', 'ckey', 'csecret')
        self.assertRaises(ValidationException, api.method)
        self.assertFalse(api.called)

    def test_success(self):
        auth = BasicAuthorizer('username', 'password')
        api = self.MyAPI()
        api._auth = auth
        api.method()
        self.assertTrue(api.called)

    def test_success_with_subclass(self):
        class MyBasic(BasicAuthorizer):
            pass
        auth = MyBasic('username', 'password')
        api = self.MyAPI()
        api._auth = auth
        api.method()
        self.assertTrue(api.called)
