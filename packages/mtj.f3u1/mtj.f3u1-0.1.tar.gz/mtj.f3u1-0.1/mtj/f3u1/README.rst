Examples
--------

Using a predefined unit::

    >>> from mtj.f3u1.units import Time
    >>> value = Time(second=90210)
    >>> print value
    1 day, 1 hour, 3 minutes, 30 seconds

Or create your own group of units::

    >>> from mtj.f3u1.factory import UnitGroup
    >>> Custom = UnitGroup(base_unit='one', ratios={
    ...     'thousand': 1000,
    ...     'hundred': 100,
    ...     'ten': 10,
    ... })
    >>> custom = Custom(thousand=2, hundred=5, one=621)
    >>> print custom
    3 thousand, 1 hundred, 2 ten, 1 one

Resolution limitation can be done also::

    >>> value = Time('hour', second=99999)
    >>> print value
    1 day, 3 hours

Construction of the value can use any key as part of the defined set of
units::

    >>> value = Time(hour=1, minute=99999)
    >>> print value
    69 days, 11 hours, 39 minutes

Any unit definitions can be respecified, along with their associated
plural form::

    >>> TimeWithWeek = Time.respecify({'week': 604800},
    ...     plurals={'week': 'weeks'})
    >>> value = TimeWithWeek(hour=1, minute=99999)
    >>> print value
    9 weeks, 6 days, 11 hours, 39 minutes

Note: currently the values are all limited to positive integers.  This
may change to be more inclusive in the future.  Maybe if I go insane I
might add a full blown units conversion and mathematics into here.
