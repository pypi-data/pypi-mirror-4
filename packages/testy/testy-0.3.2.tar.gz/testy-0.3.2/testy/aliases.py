#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""Some abbreviated shortcuts to common assertions.

For particularly lazy people who would rather type::

    import testy as t
    with t.raises(AssertionError):
        t.lt(3, 2)

than::

    from testy.assertions import assert_raises, assert_lt
    with assert_raises(AssertionError):
        assert_lt(3, 2)

"""

from __future__ import absolute_import

from .assertions import (
    assert_raises, assert_raises_and_contains, assert_equal,
    assert_almost_equal, assert_within_tolerance, assert_not_equal, assert_lt,
    assert_lte, assert_gt, assert_gte, assert_in_range, assert_between,
    assert_in, assert_not_in, assert_all_in, assert_starts_with,
    assert_not_reached, assert_rows_equal, assert_length,
    assert_is, assert_is_not, assert_all_match_regex, assert_match_regex,
    assert_any_match_regex, assert_all_not_match_regex, assert_sets_equal,
    assert_dicts_equal, assert_dict_subset, assert_subset, assert_list_prefix,
    assert_sorted_equal, assert_isinstance, assert_datetimes_equal,
    assert_exactly_one
)

raises = assert_raises
eq = assert_equal
equals = eq
equal = eq
ne = assert_not_equal
not_equal = ne
lt = assert_lt
lte = assert_lte
gt = assert_gt
gte = assert_gte
in_range = assert_in_range
between = in_range
in_seq = assert_in
not_in_seq = assert_not_in
not_in = not_in_seq
all_in = assert_all_in
regex = assert_match_regex
