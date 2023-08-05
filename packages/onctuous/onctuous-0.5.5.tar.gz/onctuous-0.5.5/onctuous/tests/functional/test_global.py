# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Ludia Inc.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Jean-Tiare Le Bigot <jtlebigot@socialludia.com>


import unittest, mock

class TestGlobal(unittest.TestCase):
    def test_nested_data(self):
        from onctuous import InvalidList, Schema, All, Coerce, Any

        data1 = {
            'exclude': ['Users', 'Uptime'],
            'include': [],
            'set': {
                'snmp_community': 'public',
                'snmp_timeout': 15,
                'snmp_version': '2c',
            },
            'targets': {
                'localhost': {
                    'exclude': ['Uptime'],
                    'features': {
                        'Uptime': {
                            'retries': 3,
                        },
                        'Users': {
                            'snmp_community': 'monkey',
                            'snmp_port': 15,
                        },
                    },
                    'include': ['Users'],
                    'set': {
                        'snmp_community': 'monkeys',
                    },
                },
            },
        }

        data2 = {
            'set': {
                'snmp_community': 'public',
                'snmp_version': '2c',
            },
            'targets': {
                'exclude': ['Ping'],
                'features': {
                    'Uptime': {'retries': 3},
                    'Users': {'snmp_community': 'monkey'},
                },
            },
        }

        settings = {
          'snmp_community': str,
          'retries': int,
          'snmp_version': All(Coerce(str), Any('3', '2c', '1')),
        }
        features = ['Ping', 'Uptime', 'Http']
        validate = Schema({
           'exclude': features,
           'include': features,
           'set': settings,
           'targets': {
             'exclude': features,
             'include': features,
             'features': {
               str: settings,
             },
           },
        })

        expected = {
            'set': {
                'snmp_version': '2c',
                'snmp_community': 'public',
            },
            'targets': {
                'exclude': ['Ping'],
                'features': {
                    'Uptime': {'retries': 3},
                    'Users': {'snmp_community': 'monkey'},
                }
            }
        }

        self.assertEqual(expected, validate(data2))
        self.assertRaisesRegexp(InvalidList, "@", validate, data1)
