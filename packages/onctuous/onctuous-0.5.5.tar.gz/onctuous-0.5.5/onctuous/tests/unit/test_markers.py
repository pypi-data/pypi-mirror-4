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

class TestMarkers(unittest.TestCase):
    def test_undefined(self):
        from onctuous import Undefined, UNDEFINED

        undef = Undefined()

        self.assertEqual(Undefined, type(UNDEFINED))
        self.assertEqual("...", repr(undef))
        self.assertEqual("...", str(undef))
        self.assertFalse(bool(undef))

    def test_marker_init(self):
        from onctuous import Marker

        marker = Marker(int, msg=MSG)

        self.assertEqual(int, marker.schema)
        self.assertEqual(MSG, marker.msg)

    def test_marker_str_repr(self):
        from onctuous import Marker

        marker = Marker(int, msg=MSG)

        self.assertEqual("<type 'int'>", str(marker))
        self.assertEqual("<type 'int'>", repr(marker))

    def test_marker_call(self):
        from onctuous import Marker, Invalid

        marker1 = Marker(int)
        marker2 = Marker(int, msg=MSG)

        marker1(123)
        marker2(123)

        self.assertRaisesRegexp(Invalid, "expected", marker1, "toto")
        self.assertRaisesRegexp(Invalid, MSG, marker2, "toto")

    def test_required_init(self):
        from onctuous import Required

        marker = Required(int, default="Yeah !", msg=MSG)

        self.assertEqual(int, marker.schema)
        self.assertEqual(MSG, marker.msg)
        self.assertEqual("Yeah !", marker.default)



