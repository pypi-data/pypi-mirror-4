This script can be used as library to split division it to simple steps or as
console script to visualise division.

Example usage as command line script::

    $ python3 -m longdivision 1/3
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

    $ python3 -m longdivision 6359/17
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

Example usage as library::

    >>> import longdivision
    >>> list(longdivision.divide_integer_part(5, 2))
    [(5, 4, 2, 1)]
    >>> list(longdivision.divide_integer_part(1, 3))
    [(1, 0, None, 1)]
    >>> list(longdivision.divide_fractional_part(1, 3))
    [(10, 9, 3), (10, 9, 3), (10, 9, 3), (10, 9, 3)]

``divide_integer_part``
    Iterates over all division steps providing ``reminder``, ``quotient``,
    ``result_digit``, ``numerator_position``.

``divide_fractional_part``
    iterates over fractional part. Each iteration returns same results as
    ``divide_integer_part`` escape last ``numerator_position``. Reminder
    argument for this function must be taken from last ``divide_integer_part``
    iteration.
