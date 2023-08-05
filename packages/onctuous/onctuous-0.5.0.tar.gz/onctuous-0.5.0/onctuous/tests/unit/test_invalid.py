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
MSG1 = "msg 1"
MSG2 = "msg 2"
PATH = ["path", "to", "error"]
FULL_MSG = "custom msg @ data['path']['to']['error']"
ERRORS = [KeyError(MSG1), ValueError(MSG2)]


class TestInvalid(unittest.TestCase):
    def test_invalid_init(self):
        from onctuous import Invalid

        inv = Invalid(MSG, PATH)

        self.assertEqual((MSG,), inv.args)
        self.assertEqual(MSG, inv.message)
        self.assertEqual(PATH, inv.path)

    def test_invalid_msg(self):
        from onctuous import Invalid

        inv = Invalid(MSG, PATH)
        self.assertEqual(MSG, inv.msg)

    def test_str(self):
        from onctuous import Invalid

        self.assertEqual(MSG, str(Invalid(MSG)))
        self.assertEqual(FULL_MSG, str(Invalid(MSG, PATH)))


class TestInvalidList(unittest.TestCase):
    def test_invalid_list_init(self):
        from onctuous import InvalidList

        self.assertEqual(ERRORS, InvalidList(ERRORS).errors)
        self.assertRaises(ValueError, InvalidList, [])

    def test_invalid_list_msg(self):
        from onctuous import InvalidList, Invalid

        self.assertEqual(MSG1, InvalidList([Invalid(MSG1)]).msg)

    def test_invalid_list_path(self):
        from onctuous import InvalidList, Invalid

        self.assertEqual([], InvalidList([Invalid(MSG1)]).path)
        self.assertEqual(PATH, InvalidList([Invalid(MSG1, PATH)]).path)

    def test_invalid_list_add(self):
        from onctuous import InvalidList, Invalid

        inv1 = Invalid(MSG1)
        inv2 = Invalid(MSG2)

        invlist = InvalidList([inv1])
        invlist.add(inv2)

        self.assertEqual([inv1, inv2], invlist.errors)

