#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__title__ = 'testy'
__version__ = '0.3.1'
__description__ = 'Python unittest helpers adapted from Testify'
__url__ = 'https://github.com/jimr/testy'
__author__ = 'James Rutherford'
__licence__ = 'MIT'
__copyright__ = 'Copyright 2012 James Rutherford'

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

from .aliases import (
    raises, eq, equals, equal, ne, not_equal, lt, lte, gt, gte, in_range,
    between, in_seq, not_in_seq, not_in, all_in, regex, 
)
