#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is almost entirely borrowed from
# https://github.com/Yelp/Testify/blob/master/testify/assertions.py
# The only modfifications are for py3k support
from __future__ import absolute_import, with_statement

import contextlib
import re
import sys

from . import utils

try:
    STRING_TYPE = basestring
except: # py3k
    STRING_TYPE = str


def _val_subtract(val1, val2, dict_subtractor, list_subtractor):
    """
    Find the difference between two container types

    Returns:

    The difference between the values as defined by list_subtractor() and
    dict_subtractor() if both values are the same container type.

    None if val1 == val2
    val1 if type(val1) != type(val1)
    Otherwise - the difference between the values
    """

    if val1 == val2:
        # if the values are the same, return a degenerate type
        # this case is not used by list_subtract or dict_subtract
        return type(val1)()

    if isinstance(val1, dict) and isinstance(val2, dict):
        val_diff = dict_subtractor(val1, val2)
    elif isinstance(val1, (list, tuple)) and isinstance(val2, (list, tuple)):
        val_diff = list_subtractor(val1, val2)
    else:
        val_diff = val1

    return val_diff


def _dict_subtract(dict1, dict2):
    """
    Return key,value pairs from dict1 that are not in dict2

    Returns:
    A new dict 'res_dict' with the following properties:

    For all (key, val) pairs where key appears in dict2:

    if dict1[val] == dict2[val] then res_dict[val] is not defined
    else res_dict[val] == dict1[val]

    If vals are themselves dictionaries the algorim is applied recursively.

    Example:
        _dict_subtract({
                       1: 'one',
                       2: 'two',
                       3: {'a': 'A', 'b': 'B'},
                       4: {'c': 'C', 'd': 'D'}
                      },
                      {
                       2: 'two',
                       3: {'a': 'A', 'b': 'B'},
                       4: {'d': 'D'},
                       5: {'e': 'E'}
                      }) => {1: 'one', 4: {'c': 'C'}}
    """

    # make a result we can edit
    result = dict(dict1)

    # find the common keys -- i.e., the ones we might need to subtract
    common_keys = set(dict1.keys()) & set(dict2.keys())
    for key in common_keys:
        val1, val2 = dict1[key], dict2[key]

        if val1 == val2:
            # values are the same: subtract
            del result[key]
        else:
            # values are different: set the output key to the different between the values
            result[key] = _val_subtract(val1, val2, _dict_subtract, _list_subtract)

    return result


def _list_subtract(list1, list2):
    """
    Returns the difference between list1 and list2.

    _list_subtract([1,2,3], [3,2,1]) == [1,3]

    If any items in the list are container types, the method recursively calls
    itself or _dict_subtract() to subtract the child
    containers.
    """

    # call val_subtract on all items that are not the same
    res_list = [_val_subtract(val1, val2, _dict_subtract, _list_subtract)
                for val1, val2 in zip(list1, list2) if val1 != val2]

    # now append items that come after any item in list1
    res_list += list1[len(list2):]

    # return a tuple of list1 is a tuple
    if isinstance(list1, tuple):
        return tuple(res_list)
    else:
        return res_list


def assert_raises(*args, **kwargs):
    """Assert an exception is raised as a context manager or by passing in a
    callable and its arguments.

    As a context manager:
    >>> with assert_raises(Exception):
    ...     raise Exception

    Pass in a callable:
    >>> def raise_exception(arg, kwarg=None):
    ...     raise Exception
    >>> assert_raises(Exception, raise_exception, 1, kwarg=234)
    """
    if (len(args) == 1) and not kwargs:
        return _assert_raises_context_manager(args[0])
    else:
        return _assert_raises(*args, **kwargs)


def assert_raises_and_contains(expected_exception_class, strings, callable_obj, *args, **kwargs):
    """Assert an exception is raised by passing in a callable and its
    arguments and that the string representation of the exception
    contains the case-insensetive list of passed in strings.

    Args
        strings -- can be a string or an iterable of strings
    """
    try:
        callable_obj(*args, **kwargs)
    except:
        _, e, _ = sys.exc_info()
        assert_isinstance(e, expected_exception_class)
        message = str(e).lower()
        if isinstance(strings, STRING_TYPE):
            strings = [strings]
        for string in strings:
            assert_in(string.lower(), message)
    else:
        assert_not_reached("No exception was raised (expected %s)" % expected_exception_class)


@contextlib.contextmanager
def _assert_raises_context_manager(exception_class):
    try:
        yield
    except:
        _, ex, _ = sys.exc_info()
        assert_isinstance(ex, exception_class)
    else:
        assert_not_reached("No exception was raised (expected %r)" %
                           exception_class)


def _assert_raises(exception_class, callable, *args, **kwargs):
    with _assert_raises_context_manager(exception_class):
        callable(*args, **kwargs)


def _diff_message(lhs, rhs):
    """If `lhs` and `rhs` are strings, return the a formatted message
    describing their differences. If they're not strings, describe the
    differences in their `repr()`s.

    NOTE: Only works well for strings not containing newlines.
    """
    lhs = repr(lhs) if not isinstance(lhs, STRING_TYPE) else lhs
    rhs = repr(rhs) if not isinstance(rhs, STRING_TYPE) else rhs

    return 'Diff:\nl: %s\nr: %s' % utils.highlight(lhs, rhs)


def assert_equal(lval, rval, message=None):
    """Assert that lval and rval are equal."""
    if message:
        assert lval == rval, message
    else:
        assert lval == rval, \
            "assertion failed: l == r\nl: %r\nr: %r\n\n%s" % \
                (lval, rval, _diff_message(lval, rval))

assert_equals = assert_equal


def assert_almost_equal(lval, rval, digits, message=None):
    """Assert that lval and rval, when rounded to the specified number of digits, are the same."""
    real_message = message or "%r !~= %r" % (lval, rval)
    assert round(lval, digits) == round(rval, digits), real_message


def assert_within_tolerance(lval, rval, tolerance, message=None):
    """Assert that the difference between the two values, as a fraction of the left value, is smaller than the tolerance specified.
    That is, abs(float(lval) - float(rval)) / float(lval) < tolerance"""
    real_message = message or "%r !~= %r" % (lval, rval)
    assert abs(float(lval) - float(rval)) / float(lval) < tolerance, real_message


def assert_not_equal(lval, rval, message=None):
    """Assert that lval and rval are unequal to each other."""
    assert lval != rval, message or 'assertion failed: %r != %r' % (lval, rval)


def assert_lt(lval, rval, message=None):
    """Assert that lval is less than rval."""
    assert lval < rval, message or 'assertion failed: %r < %r' % (lval, rval)


def assert_lte(lval, rval, message=None):
    """Assert that lval is less than or equal to rval"""
    assert lval <= rval, message or 'assertion failed: %r <= %r' % (lval, rval)


def assert_gt(lval, rval, message=None):
    """Assert that lval is greater than rval."""
    assert lval > rval, message or 'assertion failed: %r > %r' % (lval, rval)


def assert_gte(lval, rval, message=None):
    """Assert that lval is greater than or equal to rval"""
    assert lval >= rval, message or 'assertion failed: %r >= %r' % (lval, rval)


def assert_in_range(val, start, end, message=None, inclusive=False):
    """Assert that val is greater than start and less than end. If inclusive is true, val may be equal to start or end."""
    if inclusive:
        real_message = message or "! %s <= %r <= %r" % (start, val, end)
        assert start <= val <= end, real_message
    else:
        real_message = message or "! %s < %r < %r" % (start, val, end)
        assert start < val < end, real_message


def assert_between(a, b, c):
    """Assert that b is between a and c, inclusive."""
    assert_in_range(b, a, c, inclusive=True)


def assert_in(item, sequence, message=None):
    """Assert that the item is in the sequence."""
    if not message:
        message = (
            "assertion failed: expected %(item)r in %(sequence)r" % locals()
        )
    assert item in sequence, message


def assert_not_in(item, sequence, message=None):
    """Assert that the item is not in the sequence."""
    assert item not in sequence, (
        "assertion failed: expected %(item)r not in %(sequence)r" % locals()
    )


def assert_all_in(left, right):
    """Assert that everything in `left` is also in `right`
    Note: This is different than `assert_subset()` because python sets use
    `__hash__()` for comparision whereas `in` uses `__eq__()`.
    """
    unmatching = []
    for item in left:
        if item not in right:
            unmatching.append(item)
    if unmatching:
        raise AssertionError(
            "%(unmatching)r missing from %(right)r" % locals()
        )


def assert_starts_with(val, prefix, message=None):
    """Assert that val starts with prefix.

    Applies to any iterable, not just strings.

    """
    try:
        iter(val)
    except:
        raise TypeError("%(val)r is not iterable" % locals())

    try:
        iter(prefix)
    except:
        raise TypeError("%(prefix)r is not iterable" % locals())

    msg = message or "%(val)r does not start with %(prefix)r" % locals()
    for i, (l, r) in enumerate(zip(val, prefix)):
        assert_equal(l, r, msg)

    msg = (
        message or
        "%(val)r shorter than %(prefix)r, so can't start with it" % locals()
    )
    length = len(list(prefix))
    assert_equal(length, i + 1, msg)


def assert_not_reached(message=None):
    """Raise an AssertionError with a message."""
    if message:
        assert False, message
    else:
        assert False, 'egads! this line ought not to have been reached'


def assert_rows_equal(rows1, rows2):
    """Check that two sequences contain the same lists of dictionaries"""

    def norm_row(row):
        if isinstance(row, dict):
            return tuple((k, row[k]) for k in sorted(row))
        else:
            return tuple(sorted(row))

    def norm_rows(rows):
        return tuple(sorted(norm_row(row) for row in rows))

    assert_equal(norm_rows(rows1), norm_rows(rows2))


def assert_length(sequence, expected, message=None):
    """Assert a sequence or iterable has an expected length."""
    length = len(list(sequence))
    assert length == expected, (message or
        "%(sequence)s has length %(length)s expected %(expected)s" % locals()
    )


def assert_is(left, right, message=None):
    """Assert that left and right are the same object"""
    assert left is right, (
        message or "expected %(left)r is %(right)r" % locals()
    )


def assert_is_not(left, right, message=None):
    """Assert that left and right are not the same object"""
    assert left is not right, (
        message or "expected %(left)r is not %(right)r" % locals()
    )


def assert_all_match_regex(pattern, values, message=None):
    """Assert that all values in an iterable match a regex pattern.

    Args:
    pattern -- a regex.
    values -- an iterable of values to test.

    Raises AssertionError if any value does not match.

    """
    for value in values:
        if not message:
            message = "expected %(value)r to match %(pattern)r" % locals()
        assert re.match(pattern, value), message


def assert_match_regex(pattern, value, *args, **kwargs):
    """Assert that a single value matches a regex pattern."""
    assert_all_match_regex(pattern, [value], *args, **kwargs)

assert_matches_regex = assert_match_regex


def assert_any_match_regex(pattern, values, message=None):
    """Assert that at least one value in an iterable matches a regex pattern.

    Args:
    pattern -- a regex.
    values -- an iterable of values to test.

    Raises AssertionError if all values don't match.

    """
    for value in values:
        if re.match(pattern, value) is not None:
            return

    if not message:
        message = (
            "expected at least one %(values)r to match %(pattern)r" % locals()
        )
    raise AssertionError(message)


def assert_all_not_match_regex(pattern, values, message=None):
    """Assert that all values don't match a regex pattern.

    Args:
    pattern -- a regex.
    values -- an iterable of values to test.

    Raises AssertionError if any values matches.

    """
    for value in values:
        if not message:
            message = "expected %(value)r to not match %(pattern)r" % locals()
        assert not re.match(pattern, value), message

assert_none_match_regex = assert_all_not_match_regex


def assert_sets_equal(left, right, message=None):
    """Assert that two sets are equal."""
    if left != right:
        extra_left = left - right
        extra_right = right - left
        if not message:
            message = (
                "expected %(left)r == %(right)r "
                "[left has:%(extra_left)r, "
                "right has:%(extra_right)r]"
            ) % locals()
        raise AssertionError(message)


def assert_dicts_equal(left, right, ignore_keys=None, message=None):
    """Assert that two dictionarys are equal (optionally ignoring certain keys)."""
    if ignore_keys is not None:
        left = dict((k, left[k]) for k in left if k not in ignore_keys)
        right = dict((k, right[k]) for k in right if k not in ignore_keys)

    if left == right:
        return

    extra_left = _dict_subtract(left, right)
    extra_right = _dict_subtract(right, left)
    if not message:
        message = (
            "expected %(left)r == %(right)r "
            "[left has:%(extra_left)r, "
            "right has:%(extra_right)r]"
        ) % locals()
    raise AssertionError(message)


def assert_dict_subset(left, right, message=None):
    """Assert that a dictionary is a strict subset of another dictionary.

    Checks both keys and values.

    """
    difference_dict = _dict_subtract(left, right)

    if not difference_dict:
        return

    extra_left = difference_dict
    small_right = dict((k, right[k]) for k in right if k in list(left.keys()))
    extra_right = _dict_subtract(small_right, left)

    if not message:
        message = (
            "[subset has:%(extra_left)r, superset has:%(extra_right)s]"
        ) % locals()
    raise AssertionError(message)


def assert_subset(left, right, message=None):
    """Assert that the left set is a subset of the right set."""
    set_left = set(left)
    set_right = set(right)
    if not (set_left <= set_right):
        extra = set_left - set_right
        if not message:
            message = (
                "expected %(set_left)r <= %(set_right)r [left has:%(extra)r]"
            ) % locals()
        raise AssertionError(message)


def assert_list_prefix(left, right, message=None):
    """Assert that the left list is a prefix of the right list."""
    assert_equal(left, right[:len(left)], message)


def assert_sorted_equal(left, right, **kwargs):
    """Assert equality, but without respect to ordering of elements. Basically for multisets."""
    assert_equal(sorted(left), sorted(right), **kwargs)


def assert_isinstance(object_, type_, message=None):
    """Assert that an object is an instance of a given type."""
    if not message:
        message = "Expected type %r but got type %r" % (type_, type(object_))
    assert isinstance(object_, type_), message


def assert_datetimes_equal(a, b, message=None):
    """Tests for equality of times by only testing up to the millisecond."""
    assert_equal(
        a.utctimetuple()[:-3],
        b.utctimetuple()[:-3],
        message or "%r != %r" % (a, b)
    )


def assert_exactly_one(*args, **kwargs):
    """Assert that only one of the given arguments passes the provided truthy function (non-None by default).

    Args:
        truthy_fxn: a filter to redefine truthy behavior. Should take an object and return
        True if desired conditions are satisfied. For example:

        >>> assert_exactly_one(True, False, truthy_fxn=bool) # Success

        >>> assert_exactly_one(0, None) # Success

        >>> assert_exactly_one(True, False)
        AssertionError

    Returns:
        The argument that passes the truthy function
    """
    truthy_fxn = kwargs.pop('truthy_fxn', lambda x: x is not None)
    assert not kwargs, "Unexpected kwargs: %r" % kwargs

    true_args = [arg for arg in args if truthy_fxn(arg)]
    if len(true_args) != 1:
        raise AssertionError("Expected exactly one True (got %d) args: %r" % (len(true_args), args))

    return true_args[0]
