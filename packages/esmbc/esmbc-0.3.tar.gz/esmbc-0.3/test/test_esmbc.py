#!C/usr/bin/env python
"""
test_esmbc
~~~~~~~~~~

Test file for esmbc

:copyright: (c) 2012 Stuart Baker
:license: GNU GPL Version 3, see LICENSE

"""
import unittest
import os
from esmbc import cli as esmbc


class TestEsmbc(unittest.TestCase):

    def test_load_ship_dict(self):
        # data/test_ships.json:
        # {
        #     "zephyr":5000.0
        # }
        volumes = {'zephyr': 5000.0}

        test_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(test_dir, 'test_ships.json')

        self.assertEqual(esmbc.load_volumes(filename), volumes)

        self.assertRaises(FileNotFoundError, esmbc.load_volumes, '')
        self.assertRaises(FileNotFoundError, esmbc.load_volumes, 42)
        self.assertRaises(FileNotFoundError, esmbc.load_volumes, 'foo.json')

    def test_parse_ship_pairs(self):
        pairs = ['foo:1', 'BAR:2']
        expected = {'foo': '1', 'bar': '2'}

        self.assertDictEqual(expected,
                             esmbc.parse_ship_pairs(pairs))

        self.assertIsNone(esmbc.parse_ship_pairs('foo'))
        self.assertIsNone(esmbc.parse_ship_pairs([]))
        self.assertIsNone(esmbc.parse_ship_pairs(None))
        self.assertIsNone(esmbc.parse_ship_pairs(''))

    def test_calculate_volume_totals(self):
        volumes = {'zephyr': 5000.0}
        counts = {'zephyr': '2'}
        totals = {'zephyr': 10000}

        self.assertDictEqual(esmbc.calculate_volume_totals(counts, volumes),
                             totals)
        self.assertIsNone(esmbc.calculate_volume_totals({'foo': '1'},
                                                        volumes))
        self.assertIsNone(esmbc.calculate_volume_totals({'foo': '1'},
                                                        volumes))
        self.assertIsNone(esmbc.calculate_volume_totals({'zephyr': 'bar'},
                                                        volumes))
        self.assertIsNone(esmbc.calculate_volume_totals({},
                                                        volumes))

    def test_format_table(self):
        totals = {'zephyr': 10000, 'vexor_navy_issue': 112000}

        table = 'Vexor Navy Issue: 112,000m3\n'
        table = '{}Zephyr: 10,000m3\n'.format(table)
        table = '{}Total: 122,000m3'.format(table)

        self.assertEqual(esmbc.format_table(totals), table)
        self.assertIsNone(esmbc.format_table({}))

    def test_pretty_ship(self):
        self.assertEqual(esmbc.pretty_ship('vexor_navy_issue'),
                         'Vexor Navy Issue')
        self.assertEqual(esmbc.pretty_ship('zephyr'),
                         'Zephyr')
        self.assertEqual(esmbc.pretty_ship(''), '')


if __name__ == "__main__":
    unittest.main()
