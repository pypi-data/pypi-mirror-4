'''
djangoutillib/utils

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


def get_choice_name(choices, value):
    '''
    Return the human readable name of the specified database value.

    Arguments:
        choices (tuple of 2-tuples): django CHOICES constant that may contain
                groups
        value (any valid database field type): database value
    Returns:
        human readable name (string)
    Raises:
        KeyError if value is not found in choices (not even grouped)

    NOTE:
        * don't use this with the database, use get_FIELD_display() instead.
        * if choices has multiple 'keys' with the same name, the last one is 
            returned
    '''
    try:
        return dict(choices)[value]
    except KeyError:
        return dict(degroup_choices(choices))[value]


def get_choice_value(choices, name):
    '''
    Return the database value of the specified human readable name.

    Arguments:
        choices (tuple of 2-tuples): django CHOICES constant that may contain
                groups
        name (string): human readable value
    Returns:
        database value (any valid database field type)
    Raises:
        KeyError if name is not found in choices (not even grouped)

    NOTE:
        * if choices has multiple 'values' that are the same, the key of the 
            last one is returned
    '''
    try:
        return dict((v, k) for k, v in choices)[name]
    except KeyError:
        return dict((v, k) for k, v in degroup_choices(choices))[name]


def degroup_choices(grouped_choices):
    '''
    Returns a version of grouped_choices with its groups removed.

    Arguments:
        choices (tuple of 2-tuples): django CHOICES constant that may contain
                groups
    Returns:
        choices (tuple of 2-tuples): django CHOICES constant that does not
                contain groups
    Raises:
        -
    '''
    choices = []
    for group in grouped_choices:
        if isinstance(group[1], tuple):
            choices.extend(group[1])
        else:
            choices.append(group)
    return choices
