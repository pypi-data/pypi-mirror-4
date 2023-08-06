# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from unittest import TestCase

from piston_mini_client.serializers import JSONSerializer, FormSerializer
from piston_mini_client import PistonSerializable

try:
    # Python 3.
    from urllib.parse import parse_qs
except ImportError:
    # Python 2.
    from urlparse import parse_qs


class JSONSerializerTestCase(TestCase):
    def test_simple_serialize(self):
        serializer = JSONSerializer()
        self.assertEqual('{"foo": "bar"}', serializer.serialize(
            {'foo': 'bar'}))

    def test_piston_serializable_serialize(self):
        class MySerializable(PistonSerializable):
            _atts = ('foo',)

        myarg = MySerializable(foo='bar')
        serializer = JSONSerializer()
        self.assertEqual('{"foo": "bar"}', serializer.serialize(myarg))

    def test_serialize_fail(self):
        serializer = JSONSerializer()
        self.assertRaises(TypeError, serializer.serialize, {'foo': 3 + 1j})


class FormSerializerTestCase(TestCase):
    def test_simple_serialize(self):
        serializer = FormSerializer()
        self.assertEqual('foo=bar', serializer.serialize({'foo': 'bar'}))

    def test_piston_serializable_serialize(self):
        class MySerializable(PistonSerializable):
            _atts = ('foo', 'bar')

        myarg = MySerializable(foo='baz', bar=42)
        serializer = FormSerializer()
        # Argument order is undefined, so parse these into dictionaries which
        # can be compared.
        want = parse_qs('foo=baz&bar=42')
        got = parse_qs(serializer.serialize(myarg))
        self.assertEqual(want, got)

    def test_serialize_nested(self):
        # Maybe we should flatly refuse to serialize nested structures?
        serializer = FormSerializer()
        self.assertEqual('foo=%7B%27a%27%3A+%27b%27%7D',
                         serializer.serialize({'foo': {'a': 'b'}}))
