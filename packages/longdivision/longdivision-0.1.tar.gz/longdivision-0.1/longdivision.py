#!/usr/bin/env python3

# longdivision - breaks down a division problem into a series of easier steps.
# Copyright (C) 2012  Mantas Zimnickas <sirexas@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

DEFAULT_PRECISION = 4


def splitdigits(n):
    """
    >>> splitdigits(6357)
    [6, 3, 5, 7]
    """
    digits = []
    while n:
        digits.insert(0, n % 10)
        n //= 10
    return digits


def floattofraction(f):
    """
    >>> floattofraction(0.3)
    (3, 10)
    >>> floattofraction(2.5)
    (25, 10)
    >>> floattofraction(2)
    (2, 1)
    >>> floattofraction(1.0)
    (1, 1)
    >>> floattofraction(0.1)
    (1, 10)
    """
    fstr = str(f)
    if '.' in fstr:
        integer, numerator = str(fstr).split('.')
    else:
        return int(f), 1
    if int(numerator):
        fraction_len = len(numerator)
    else:
        fraction_len = 0
    denominator = 10**fraction_len
    numerator = (int(integer) * denominator) + (int(numerator) or 0)
    return  numerator, denominator


def shift_digits(n, digits):
    """
    >>> shift_digits(21, [2, 2, 3, 4])
    (2, [2, 3, 4], 1)
    """
    shift = 0
    for i, digit in enumerate(digits):
        _shift = shift * 10 + digit
        if _shift >= n:
            return shift, digits[i:], i
        shift = _shift
    return shift, [], i


def divide_integer_part(numerator, denominator):
    """
    >>> list(divide_integer_part(6357, 3))
    [(6, 6, 2, 0), (3, 3, 1, 1), (5, 3, 1, 2), (27, 27, 9, 3)]
    >>> list(divide_integer_part(1, 3))
    [(1, 0, 0, 0)]
    """
    quotient = 0
    reminder, digits, i = shift_digits(denominator, splitdigits(numerator))
    for i, digit in enumerate(digits, i):
        reminder = reminder * 10 + digit
        result_digit = reminder // denominator
        quotient = result_digit * denominator
        yield reminder, quotient, result_digit, i
        reminder = reminder - quotient

    if numerator < denominator:
        yield reminder, quotient, 0, i


def divide_fractional_part(reminder, denominator, precision=DEFAULT_PRECISION):
    """
    >>> list(divide_fractional_part(1, 3))
    [(10, 9, 3), (10, 9, 3), (10, 9, 3), (10, 9, 3)]
    """
    i = 0
    while reminder > 0 and i < precision:
        reminder = reminder * 10
        result_digit = reminder // denominator
        quotient = result_digit * denominator
        yield reminder, quotient, result_digit
        reminder = reminder - quotient
        i += 1


def format_step(indent, denominator, reminder, quotient, digit):
    first_step = indent == 2
    reminder = '{:0{}}'.format(reminder, 1 if first_step else 2)
    return [
        '_{}'.format(reminder).rjust(indent),
        '{:>{}}  <- {} * {}'.format(quotient, indent, digit, denominator),
        ('-' * len(reminder)).rjust(indent),
    ]


def print_long_division(numerator, denominator, precision=DEFAULT_PRECISION):
    """
    >>> print_long_division(6357, 3)
    _6357 / 3 = 2119
     6  <- 2 * 3
     -
    _03
      3  <- 1 * 3
     --
     _05
       3  <- 1 * 3
      --
      _27
       27  <- 9 * 3
       --
        0
    >>> print_long_division(1, 3)
    _1 / 3 = 0.3333
     0  <- 0 * 3
     -
    _10
      9  <- 3 * 3
     --
     _10
       9  <- 3 * 3
      --
      _10
        9  <- 3 * 3
       --
       _10
         9  <- 3 * 3
        --
         1
    >>> print_long_division(1, 1000)
    _1 / 1000 = 0.001
     0  <- 0 * 1000
     -
    _10
      0  <- 0 * 1000
     --
    _100
       0  <- 0 * 1000
     ---
    _1000
     1000  <- 1 * 1000
     ----
        0
    >>> print_long_division(6359, 17)
    _6359 / 17 = 374.0588
     51  <- 3 * 17
     --
    _125
     119  <- 7 * 17
     ---
      _69
       68  <- 4 * 17
       --
       _10
         0  <- 0 * 17
        --
       _100
         85  <- 5 * 17
        ---
        _150
         136  <- 8 * 17
         ---
         _140
          136  <- 8 * 17
          ---
            4
    >>> print_long_division(2, 5)
    _2 / 5 = 0.4
     0  <- 0 * 5
     -
    _20
     20  <- 4 * 5
     --
      0
    >>> print_long_division(1.3, 1.4)
    _130 / 140 = 0.9285
       0  <- 0 * 140
     ---
    _1300
     1260  <- 9 * 140
     ----
      _400
       280  <- 2 * 140
       ---
      _1200
       1120  <- 8 * 140
       ----
        _800
         700  <- 5 * 140
         ---
         100
    >>> print_long_division(1, 0.1)
    _10 / 1 = 10
     1  <- 1 * 1
     -
    _00
      0  <- 0 * 1
     --
      0
    """
    a, b = floattofraction(numerator)
    c, d = floattofraction(denominator)
    numerator, denominator = a * d, b * c

    lines = []
    result = ''

    # Divide integer part
    itr = divide_integer_part(numerator, denominator)
    for reminder, quotient, digit, position in itr:
        indent = position + 2
        result += str(digit)
        lines += format_step(indent, denominator, reminder, quotient, digit)

    # Divide fractional part
    reminder = reminder - quotient
    if reminder > 0:
        result += '.'
        itr = divide_fractional_part(reminder, denominator, precision)
        for indent, (reminder, quotient, digit) in enumerate(itr, indent+1):
            result += str(digit)
            lines += format_step(indent, denominator, reminder, quotient, digit)

        reminder = reminder - quotient

    # Rewrite first line with final result
    lines[0] = '_{} / {} = {}'.format(numerator, denominator, result)

    # Append reminder
    lines.append(str(reminder).rjust(indent))

    print('\n'.join(lines))


def main():
    import argparse

    parser = argparse.ArgumentParser(description=(
            'Breaks down a division problem into a series of easier steps.'
        ))
    parser.add_argument('problem', help='division problem, example: 1/3')
    parser.add_argument('-p', '--precision', type=int,
                        default=DEFAULT_PRECISION, help=(
            'fraction precision (default: %d)'
        ) % DEFAULT_PRECISION)

    args = parser.parse_args()

    if '/' in args.problem:
        numerator, denominator = map(float, args.problem.split('/'))
    else:
        numerator, denominator = float(args.problem), 1

    print_long_division(numerator, denominator, args.precision)


if __name__ == '__main__':
    main()
