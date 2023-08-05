# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Ludia Inc.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Jean-Tiare Le Bigot <jtlebigot@socialludia.com>


import unittest, mock

MSG = "custom msg"

class TestValidators(unittest.TestCase):
    def test_extra(self):
        from onctuous import Extra, SchemaError

        self.assertRaises(SchemaError, Extra, "_")

    def test_msg(self):
        from onctuous import Msg, Invalid

        self.assertEqual(123, Msg(int, msg=MSG)(123))
        self.assertRaisesRegexp(Invalid, MSG, Msg(int, msg=MSG), "hello")

    def test_coerce(self):
        from onctuous import Coerce, Invalid

        self.assertRaisesRegexp(Invalid, "expected", Coerce(int), "hello")
        self.assertRaisesRegexp(Invalid, MSG, Coerce(int, MSG), "hello")

    def test_is_true(self):
        from onctuous import IsTrue, Invalid

        self.assertEqual("123", IsTrue()("123"))
        self.assertEqual(["123"], IsTrue()(["123"]))
        self.assertEqual(True, IsTrue()(True))

        self.assertRaisesRegexp(Invalid, MSG, IsTrue(MSG), "")
        self.assertRaisesRegexp(Invalid, MSG, IsTrue(MSG), [])
        self.assertRaisesRegexp(Invalid, MSG, IsTrue(MSG), {})
        self.assertRaisesRegexp(Invalid, MSG, IsTrue(MSG), False)
        self.assertRaisesRegexp(Invalid, "value", IsTrue(), False)

    def test_is_false(self):
        from onctuous import IsFalse, Invalid

        self.assertEqual("", IsFalse()(""))
        self.assertEqual([], IsFalse()([]))
        self.assertEqual(False, IsFalse()(False))

        self.assertRaisesRegexp(Invalid, MSG, IsFalse(MSG), "123")
        self.assertRaisesRegexp(Invalid, MSG, IsFalse(MSG), ["123"])
        self.assertRaisesRegexp(Invalid, MSG, IsFalse(MSG), True)
        self.assertRaisesRegexp(Invalid, "value", IsFalse(), True)

    def test_boolean(self):
        from onctuous import Boolean, Invalid

        self.assertEqual(True, Boolean()(-42))
        self.assertEqual(True, Boolean()(True))
        self.assertEqual(True, Boolean()(['toto']))
        self.assertEqual(True, Boolean()('1'))
        self.assertEqual(True, Boolean()('trUe'))
        self.assertEqual(True, Boolean()('yeS'))
        self.assertEqual(True, Boolean()('oN'))
        self.assertEqual(True, Boolean()('eNable'))

        self.assertEqual(False, Boolean()(0))
        self.assertEqual(False, Boolean()(False))
        self.assertEqual(False, Boolean()([]))
        self.assertEqual(False, Boolean()('0'))
        self.assertEqual(False, Boolean()('fALse'))
        self.assertEqual(False, Boolean()('nO'))
        self.assertEqual(False, Boolean()('oFf'))
        self.assertEqual(False, Boolean()('diSAble'))

        self.assertRaisesRegexp(Invalid, MSG, Boolean(MSG), "toto")
        self.assertRaisesRegexp(Invalid, "expected", Boolean(), "toto")

    @mock.patch('__builtin__.bool')
    def test_boolean_error(self, m_bool):
        from onctuous import Boolean, Invalid

        m_bool.side_effect = ValueError
        self.assertRaisesRegexp(Invalid, "expected", Boolean(), None)

    def test_match(self):
        from onctuous import Match, Invalid

        self.assertEqual("0x123bAc", Match("^0x[a-fA-F0-9]+$")("0x123bAc"))
        self.assertEqual("0x123bAc", Match(r"^0x[a-fA-F0-9]+$")("0x123bAc"))

        self.assertRaisesRegexp(Invalid, MSG, Match("^0x[a-fA-F0-9]+$", MSG), "toto")
        self.assertRaisesRegexp(Invalid, "match", Match("^0x[a-fA-F0-9]+$"), "toto")

    def test_sub(self):
        from onctuous import Sub

        self.assertEqual("Hi You!", Sub("toto", "Chuck")("Hi You!"))
        self.assertEqual("Hi Chuck!", Sub("You", "Chuck")("Hi You!"))
        self.assertEqual("Hi Chuck!", Sub("[Yy]ou", "Chuck")("Hi you!"))
        self.assertEqual("Hi Chuck!", Sub(r"[Yy]ou", "Chuck")("Hi you!"))

    def test_url(self):
        from onctuous import Url, Invalid

        self.assertEqual("www.example.com", Url()("www.example.com"))
        self.assertEqual("www.example.com/my/resource", Url()("www.example.com/my/resource"))
        self.assertEqual("www.example.com:42/", Url()("www.example.com:42/"))
        self.assertEqual("toto://www.example.com:42/", Url()("toto://www.example.com:42/"))
        self.assertEqual("toto://jt@www.example.com:42/", Url()("toto://jt@www.example.com:42/"))
        self.assertEqual("toto://jt:pwd@www.example.com:42/", Url()("toto://jt:pwd@www.example.com:42/"))

        self.assertRaisesRegexp(Invalid, MSG, Url(MSG), 123)
        self.assertRaisesRegexp(Invalid, "URL", Url(), 132)

    def test_is_file(self):
        import os
        from onctuous import IsFile, Invalid

        file = os.path.abspath(__file__)
        dir = os.path.dirname(__file__)

        self.assertEqual(file, IsFile()(file))
        self.assertRaisesRegexp(Invalid, "file", IsFile(), dir)
        self.assertRaisesRegexp(Invalid, "file", IsFile(), "/tarata/@==")
        self.assertRaisesRegexp(Invalid, MSG, IsFile(MSG), "/tarata/@==")

    def test_is_dir(self):
        import os
        from onctuous import IsDir, Invalid

        file = os.path.abspath(__file__)
        dir = os.path.dirname(__file__)

        self.assertEqual(dir, IsDir()(dir))
        self.assertRaisesRegexp(Invalid, "directory", IsDir(), file)
        self.assertRaisesRegexp(Invalid, "directory", IsDir(), "/tarata/@==")
        self.assertRaisesRegexp(Invalid, MSG, IsDir(MSG), "/tarata/@==")

    def test_path_exists(self):
        import os
        from onctuous import PathExists, Invalid

        file = os.path.abspath(__file__)
        dir = os.path.dirname(__file__)

        self.assertEqual(dir, PathExists()(dir))
        self.assertEqual(file, PathExists()(file))
        self.assertRaisesRegexp(Invalid, "exist", PathExists(), "/tarata/@==")
        self.assertRaisesRegexp(Invalid, MSG, PathExists(MSG), "/tarata/@==")

    def test_in_range(self):
        from onctuous import InRange, Invalid

        self.assertEqual(3, InRange()(3))
        self.assertEqual(3, InRange(min=1)(3))
        self.assertEqual(3, InRange(max=4)(3))
        self.assertEqual(3, InRange(min=1, max=4)(3))
        self.assertEqual('ab', InRange(min='aaa', max='bbbb')('ab'))

        self.assertRaisesRegexp(Invalid, "least", InRange(min=1), -1)
        self.assertRaisesRegexp(Invalid, "least", InRange(min=1, max=3), -1)
        self.assertRaisesRegexp(Invalid, "most", InRange(max=-2), -1)
        self.assertRaisesRegexp(Invalid, MSG, InRange(max=-2, msg=MSG), -1)

    def test_clamp(self):
        from onctuous import Clamp

        self.assertEqual(3, Clamp()(3))
        self.assertEqual(3, Clamp(min=1)(3))
        self.assertEqual(3, Clamp(max=4)(3))
        self.assertEqual(3, Clamp(min=1, max=4)(3))
        self.assertEqual('ab', Clamp(min='aa', max='bbbb')('ab'))

        self.assertEqual(1, Clamp(min=1)(-1))
        self.assertEqual(4, Clamp(max=4)(12))
        self.assertEqual(1, Clamp(min=1, max=4)(-1))
        self.assertEqual('baa', Clamp(min='baa', max='bbbb')('ab'))

    def test_length(self):
        from onctuous import Length, Invalid

        self.assertEqual("Ludia", Length()("Ludia"))
        self.assertEqual("Ludia", Length(min=1)("Ludia"))
        self.assertEqual("Ludia", Length(max=10)("Ludia"))
        self.assertEqual("Ludia", Length(min=1, max=10)("Ludia"))

        self.assertRaisesRegexp(Invalid, "least", Length(min=10), "Ludia")
        self.assertRaisesRegexp(Invalid, "least", Length(min=10, max=15), "Ludia")
        self.assertRaisesRegexp(Invalid, "most", Length(max=4), "Ludia")
        self.assertRaisesRegexp(Invalid, MSG, Length(max=4, msg=MSG), "Ludia")

    def test_to_lower(self):
        from onctuous import ToLower

        self.assertEqual("ludia", ToLower("LuDiA"))

    def test_to_upper(self):
        from onctuous import ToUpper

        self.assertEqual("LUDIA", ToUpper("LuDiA"))

    def test_to_capitalize(self):
        from onctuous import Capitalize

        self.assertEqual("Ludia is awesome", Capitalize("LuDiA iS AwesOME"))

    def test_to_title(self):
        from onctuous import Title

        self.assertEqual("Ludia Is Awesome", Title("LuDiA iS AwesOME"))

    # very basic test
    def test_any(self):
        from onctuous import Any, Invalid

        self.assertEqual("toto", Any("toto", "titi")("toto"))

        self.assertRaisesRegexp(Invalid, "valid", Any("toto", "titi"), "tete")
        self.assertRaisesRegexp(Invalid, MSG, Any("toto", "titi", msg=MSG), "tete")

    # very basic test
    def test_all(self):
        from onctuous import All, Invalid

        self.assertEqual(u"toto", All(unicode, u"toto")(u"toto"))

        self.assertRaisesRegexp(Invalid, "valid", All(unicode, u"toto"), u"tete")
        self.assertRaisesRegexp(Invalid, MSG, All(unicode, u"toto", msg=MSG), u"tete")

