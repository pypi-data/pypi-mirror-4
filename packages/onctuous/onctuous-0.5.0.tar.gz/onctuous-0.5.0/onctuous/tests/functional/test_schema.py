# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Ludia Inc.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Jean-Tiare Le Bigot <jtlebigot@socialludia.com>


import unittest

MSG = "custom msg"

class TestSchema(unittest.TestCase):
    def test_dict(self):
        from onctuous import Schema, InvalidList, Coerce, Required

        validate = Schema({'one': 'two', 'three': 'four'})

        # invalid dictionary value
        self.assertRaisesRegexp(InvalidList, 'not a valid value', validate, {'one': 'three'})
        # invalid key
        self.assertRaisesRegexp(InvalidList, 'extra key', validate, {'two': 'three'})

        # validate int type
        validate = Schema({'one': 'two', 'three': 'four', int: str})
        self.assertEqual({10: 'twenty'}, validate({10: 'twenty'}))
        self.assertRaisesRegexp(InvalidList, 'extra key', validate, {'10': 'twenty'})

        # validate with type coercion
        validate = Schema({'one': 'two', 'three': 'four', Coerce(int): str})
        self.assertEqual({10: 'twenty'}, validate({'10': 'twenty'}))

        # test required key with defaults
        validate = Schema({Required(1,default='toto'):str})
        self.assertEqual({1: 'toto'}, validate({}))

    def test_list(self):
        from onctuous import Schema, InvalidList

        self.assertEqual([1,2,3], Schema([1,2,3,4,5,6])([1,2,3]))
        self.assertEqual([1,2,3], Schema([int])([1,2,3]))

        # extra entry
        self.assertRaisesRegexp(InvalidList, "value", Schema([1,2,3,4,5,6]), [0,1,2,3])


    def test_msg(self):
        from onctuous import Schema, InvalidList, Msg

        # custom message for direct descendants errors
        validate = Schema(Msg(['one', 'two', int], MSG))
        self.assertRaisesRegexp(InvalidList, MSG, validate, ['three'])

        # regular message for indirect descendants
        validate = Schema(Msg([['one', 'two', int]], MSG))
        self.assertRaisesRegexp(InvalidList, "invalid", validate, [['three']])

    def test_any_all(self):
        from onctuous import Schema, Any, All, InvalidList, Coerce

        validate = Schema(Any('true', 'false', All(Any(int, bool), Coerce(bool))))
        self.assertTrue(validate('true'))
        self.assertTrue(validate(1))
        self.assertRaisesRegexp(InvalidList, "valid", validate, "toto")

        validate = Schema(Any({int: {int:str}}, bool))
        self.assertRaises(InvalidList, validate, {1:{"2":"titi"}})

