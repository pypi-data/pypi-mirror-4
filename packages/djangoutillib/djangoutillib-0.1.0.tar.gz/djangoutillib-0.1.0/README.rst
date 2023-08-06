==============================================================
djangoutillib - collection of generic django utility functions
==============================================================

Django Utility Library is a small collection of generic functions and classes
for use with Django. Other than django there are no external dependencies.

Working with CHOICES tuples
===========================

Django provides no easy way for doing lookup in CHOICES tuples other than
``get_FIELD_display()`` in a database context. For using CHOICES tuples without
a database and for doing reverse lookup this library has two functions:
``get_choice_name`` and ``get_choice_value``. Furthermore there is a function
to 'translate' a CHOICES tuple with groups to a 'flat' tuple.
For the following examples, these CHOICES tuples are used::

    SIMPLE_CHOICES = (
            (0, 'zero'),
            (1, 'one'),
            (2, 'two'),
            (3, 'three'),
    )
    GROUPED_CHOICES = (
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

get_choice_name()
-----------------

Returns the human readable name of the specified (database) value, which works
on a flat CHOICES tuple as well as one with groups::

    >>> import djangoutillib.utils as du
    >>> du.get_choice_name(SIMPLE_CHOICES, 2)
    two
    >>> du.get_choice_name(SIMPLE_CHOICES, 5)
    KeyError: 5
    >>> du.get_choice_name(GROUPED_CHOICES, 3)
    three
    >>> du.get_choice_name(GROUPED_CHOICES, 'nogroup')
    four

get_choice_value()
------------------

Returns the (database) value of the specified human readable name, which works
on a flat CHOICES tuple as well as one with groups::

    >>> import djangoutillib.utils as du
    >>> du.get_choice_value(SIMPLE_CHOICES, 'two')
    2
    >>> du.get_choice_value(GROUPED_CHOICES, 'three')
    3
    >>> du.get_choice_value(GROUPED_CHOICES, 'four')
    nogroup
    >>> du.get_choice_value(GROUPED_CHOICES, 'five')
    KeyError: 'five'

degroup_choices()
-----------------

Returns a version of grouped_choices with its groups removed::

    >>> import djangoutillib.utils as du
    >>> du.degroup_choices(GROUPED_CHOICES)
    [(0, 'zero'), (1, 'one'), (2, 'two'), (3, 'three'), ('nogroup', 'four')]
