'''
djangoutillib/tests

Copyright (C) 2013 Edwin van Opstal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see `<http://www.gnu.org/licenses/>`.
'''

from __future__ import division
from __future__ import absolute_import

from django.test import TestCase

from djangoutillib.utils import get_choice_name, get_choice_value, \
        degroup_choices


class utilTests(TestCase):

    def setUp(self):
        self.simple_choices = (
                (0, 'zero'),
                (1, 'one'),
                (2, 'two'),
                (3, 'three'),
        )
        self.grouped_choices = (
                ('group1', (
                        (0, 'zero'),
                        (1, 'one'),
                )),
                ('group2', (
                    (2, 'two'),
                    (3, 'three'),
                )),
                ('nogroup', 'four'),
        )
        self.invalid_names_values = ('a', 'b', 'abc', 10, 11, 1.3)

    def test_get_choice_name(self):
        for name, value in self.simple_choices:
            self.assertEqual(get_choice_name(self.simple_choices, name), value)
        for name in self.invalid_names_values:
            self.assertRaises(KeyError, get_choice_name, self.simple_choices, 
                    name)
        for group, values in self.grouped_choices:
            if isinstance(values, tuple):
                for name, value in values:
                    self.assertEqual(get_choice_name(
                            self.grouped_choices, name), value)
            else:
                self.assertEqual(get_choice_name(self.grouped_choices, group), 
                            values)

    def test_get_choice_value(self):
        for name, value in self.simple_choices:
            self.assertEqual(get_choice_value(self.simple_choices, value), 
                    name)
        for value in self.invalid_names_values:
            self.assertRaises(KeyError, get_choice_value, self.simple_choices, 
                    value)
        for group, values in self.grouped_choices:
            if isinstance(values, tuple):
                for name, value in values:
                    self.assertEqual(get_choice_value(
                            self.grouped_choices, value), name)
            else:
                self.assertEqual(get_choice_value(self.grouped_choices, values), 
                            group)

    def test_degroup_choices(self):
        self.assertEqual(degroup_choices(self.simple_choices), 
                list(self.simple_choices))
        choices = degroup_choices(self.grouped_choices)
        self.assertIn(self.grouped_choices[2], choices)
        for name_value in self.simple_choices:
            self.assertIn(name_value, choices)
