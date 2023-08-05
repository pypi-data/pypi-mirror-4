# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Ludia Inc.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Jean-Tiare Le Bigot <jtlebigot@socialludia.com>


import unittest, mock

MSG1 = "msg 1"
PATH = ["path", "to", "error"]

class TestSchema(unittest.TestCase):
    def test_schema_init(self):
        from onctuous import Schema

        schema = Schema(int, required=True, extra=True)
        self.assertEqual(int, schema.schema)
        self.assertEqual(True, schema.required)
        self.assertEqual(True, schema.extra)

        schema = Schema(int)
        self.assertEqual(int, schema.schema)
        self.assertEqual(False, schema.required)
        self.assertEqual(False, schema.extra)

    @mock.patch('onctuous.Schema.validate')
    def test_schema_call(self, m_validate):
        from onctuous import Schema

        Schema(int)(123)
        m_validate.assert_called_with([], int, 123)

    @mock.patch('onctuous.Schema._validate_dict')
    @mock.patch('onctuous.Schema._validate_list')
    @mock.patch('onctuous.Schema._validate_scalar')
    def test_schema_validate_scalar(self, m_val_scalar, m_val_list, m_val_dict):
        from onctuous import Schema

        Schema(None).validate([], int, 123)

        m_val_scalar.assert_called_once_with([], int, 123)
        self.assertFalse(m_val_dict.called)
        self.assertFalse(m_val_list.called)

    @mock.patch('onctuous.Schema._validate_dict')
    @mock.patch('onctuous.Schema._validate_list')
    @mock.patch('onctuous.Schema._validate_scalar')
    def test_schema_validate_dict(self, m_val_scalar, m_val_list, m_val_dict):
        from onctuous import Schema

        Schema(None).validate([], {'a': 'b'}, {'a': 'b'})

        m_val_dict.assert_called_once_with([], {'a': 'b'}, {'a': 'b'})
        self.assertFalse(m_val_scalar.called)
        self.assertFalse(m_val_list.called)

    @mock.patch('onctuous.Schema._validate_dict')
    @mock.patch('onctuous.Schema._validate_list')
    @mock.patch('onctuous.Schema._validate_scalar')
    def test_schema_validate_list(self, m_val_scalar, m_val_list, m_val_dict):
        from onctuous import Schema

        Schema(None).validate([], ['a', 'b'], ['a', 'b'])

        m_val_list.assert_called_once_with([], ['a', 'b'], ['a', 'b'])
        self.assertFalse(m_val_scalar.called)
        self.assertFalse(m_val_dict.called)


    @mock.patch('onctuous.Schema._validate_dict')
    @mock.patch('onctuous.Schema._validate_list')
    @mock.patch('onctuous.Schema._validate_scalar')
    def test_schema_validate_scalar_error(self, m_val_scalar, m_val_list, m_val_dict):
        from onctuous import Schema, InvalidList, Invalid

        m_val_scalar.side_effect = Invalid(MSG1)
        self.assertRaisesRegexp(InvalidList, MSG1, Schema(None).validate, [], int, 123)

        m_val_scalar.side_effect = InvalidList([Invalid(MSG1)])
        self.assertRaisesRegexp(InvalidList, MSG1, Schema(None).validate, [], int, 123)

    def test_validate_scalar(self):
        from onctuous import Schema, Invalid

        # test value specification
        self.assertEqual(123, Schema._validate_scalar([], 123, 123))
        self.assertEqual("123", Schema._validate_scalar([], "123", "123"))

        # test type specification
        self.assertEqual(123, Schema._validate_scalar([], int, 123))
        self.assertEqual("123", Schema._validate_scalar([], str, "123"))

        # test callable specification
        spec = mock.Mock()
        spec.return_value = 123
        self.assertEqual(123, Schema._validate_scalar([], spec, "123"))

        # errors
        self.assertRaises(Invalid, Schema._validate_scalar, [], "toto", "123")
        self.assertRaises(Invalid, Schema._validate_scalar, [], int, "123")

        spec.side_effect = ValueError()
        self.assertRaises(Invalid, Schema._validate_scalar, [], spec, "123")
        spec.side_effect = Invalid(MSG1)
        self.assertRaisesRegexp(Invalid, MSG1, Schema._validate_scalar, [], spec, "123")

    @mock.patch('onctuous.Schema.validate')
    def test_validate_list(self, m_validate):
        from onctuous import Schema, InvalidList, Invalid

        # test with empty value
        self.assertEqual([], Schema(None)._validate_list([], [1,2,3], []))

        # test with empty condition
        self.assertEqual([1,2,3], Schema(None)._validate_list([], [], [1,2,3]))

        # regular validation path (if number seems awkward, remember: it's a mock)
        m_validate.return_value = 42
        self.assertEqual([42], Schema(None)._validate_list([], [1,2,3], [12]))
        m_validate.assert_called_with([0], 1, 12)

        # test with local error
        m_validate.side_effect = Invalid(MSG1)
        self.assertRaises(InvalidList, Schema(None)._validate_list, [], [1,2,3], [12])

        # test with deep error (sub item) (weird logic btw)
        m_validate.side_effect = Invalid(MSG1, PATH)
        self.assertRaises(Invalid, Schema(None)._validate_list, [], [1,2,3], [12])

    @mock.patch('onctuous.Schema.validate')
    def test_validate_dict(self, m_validate):
        from onctuous import Schema, InvalidList, Invalid, Required, Optional, Extra

        # test with empty schema and extra
        self.assertEqual({'1':'2'}, Schema(None, extra=True)._validate_dict([], {}, {'1':'2'}))
        self.assertRaisesRegexp(InvalidList, "extra", Schema(None)._validate_dict, [], {}, {'1':'2'})

        # test per schema extra
        self.assertEqual({'1':'2'}, Schema(None)._validate_dict([], {Extra: 'whatever'}, {'1':'2'}))

        # no key required
        self.assertEqual({}, Schema(None)._validate_dict([], {'1':'2'}, {}))

        # all key required
        m_validate.return_value = 42
        self.assertEqual({42:42}, Schema(None, required=True)._validate_dict([], {'1':'2'}, {'1':'2'}))
        self.assertRaisesRegexp(InvalidList, "required", Schema(None, required=True)._validate_dict, [], {'1':'2'}, {})

        # all key required BUT optional (sic)
        m_validate.return_value = 42
        self.assertEqual({}, Schema(None, required=True)._validate_dict([], {Optional('1'):'2'}, {}))
        self.assertEqual({42:42}, Schema(None, required=True)._validate_dict([], {Optional('1'):'2'}, {'1':'2'}))

        # individual key required
        m_validate.return_value = 42
        self.assertEqual({42:42}, Schema(None)._validate_dict([], {Required('1'):'2'}, {'1':'2'}))
        self.assertRaisesRegexp(InvalidList, "required", Schema(None)._validate_dict, [], {Required('1'):'2'}, {})
