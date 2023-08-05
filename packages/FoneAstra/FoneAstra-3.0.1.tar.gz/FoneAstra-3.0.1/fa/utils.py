#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8

import decimal
import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from fa.models import *


logger = logging.getLogger(__name__)


def convert_temp(chars):
    """Unpacks temperatures from their packed forms. Each temperature consists
    of a 12-bit two's complement number, with 1 sign bit, 7 integer bits,
    and 4 fraction bits, and is packed into two 6-bit ASCII chars.

    Arguments:
        chars   -   string of length >= 2
    """
    # Encoder string of allowable ascii chars
    encoder = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"

    # convert temp reading from ascii to decimal
    upper_ascii_char = chars[0]
    lower_ascii_char = chars[1]
    upper_int = encoder.index(upper_ascii_char)
    lower_int = encoder.index(lower_ascii_char)
    upper_bits = bin(upper_int)[2:].zfill(6)
    lower_bits = bin(lower_int)[2:].zfill(6)
    sign_bit = upper_bits[0]
    if (int(sign_bit) == 1):
        sign = "-"
    else:
        sign = "+"
    int_bits = upper_bits[1:6] + lower_bits[0:2]
    dec_bits = lower_bits[2:6]
    if (int(sign_bit) == 1):
        integer_num = int(int_bits,2) ^ int("1111111",2)
    else:
        integer_num = int(int_bits, 2)
    decimal_num = float(int(dec_bits, 2))
    if (int(sign_bit) == 1):
        fractional_dec = ((16.0 - decimal_num) / 16.0)
    else:
        fractional_dec = (decimal_num / 16.0)
    complete_num = integer_num + fractional_dec
    temp_str = "%s%.1f" % (sign, complete_num)
    temp = decimal.Decimal(temp_str)
    return temp


# This next function is copy/pasted from the old Reporters class
def field_bundles(qd, *keys):
    """When an HTML form has multiple fields with the same name, they are received
       as a single key, with an array of values -- which looks something like:

     { "backend": ["a", "b"], "identity": ["111", "222"], **other_stuff }

     ...which isn't very easy to iterate as pairs of "backend" and "identity";
     which is most often what we want to do. This method inverts the axis,
     and returns the same data in the less verbose, and more useful format:

     [("a", "111"), ("b", "222")]

     The order of tuples is preserved from the querydict - this USUALLY means
     that they'll be output in the same order as the controls on the HTML form
     that the request was triggered by - but that's not guaranteed. The order
     of the values inside the tuples (originally, the keys) is derrived from
     the *keys argument(s). Using the input from the first example, to output
     the second, in a familiar view:

     field_bundles(request.POST, "backend", "identity")"""

    bundles = []
    length = None

    # check that all values are of the same
    # length, even if that is zero, to avoid
    # creating half-bundles with missing data
    for key in keys:

        # if this is the first pair, then store the length
        # of the value, to check against subsequent pairs
        kl = len(qd.getlist(key))
        if length is None:
            length = kl

        # not the first pair, so we know long the value
        # SHOULD be - if it isn't exactly right, abort
        elif length != kl:
            raise IndexError(
                "for %s, expected length of %d, got %d" % (
                    key, length, kl))

    # iterate all of the data that we're going to
    # capture, and invert the axis, to group bundles
    # togeter, rather than parameters
    for n in range(0, length):
        bundles.append([qd.getlist(k)[n] for k in keys])

    return bundles


def chunks(iterable, n):
    """Yield successive n-sized chunks from iterable. Stolen from Ned
    Batchelder on StackOverflow.

    """
    for i in range(0, len(iterable), n):
        yield iterable[i:i+n]


def as_int(val):
    """Returns the value of the argument in hexadecimal.  Used so that
    we can abstract which base to use.

    """
    return int(val, 16)


def get_temp_sequence(readings):
    """Take in a string containing encoded temperatures and return a
    list of decimals.

    """
    return [convert_temp(x) for x in chunks(readings, 2)]


def regex_test(regex_list, input_string):
    """Given a list of (regex, object) tuples and an input string, matches
    the input string against each regex in turn and returns a tuple containing
    the object and the regex match object if the string matches. Only returns
    the first match.

    """
    for regex, obj in regex_list:
        match_obj = re.match(regex, input_string, re.IGNORECASE)
        if match_obj:
            logger.debug("Chose match {regex} for {input}".format(
                regex=regex,
                input=input_string,
            ))
            return (obj, match_obj)
    return (None, None)
