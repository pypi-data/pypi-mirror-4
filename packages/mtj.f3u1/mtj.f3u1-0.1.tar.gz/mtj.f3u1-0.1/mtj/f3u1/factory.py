from sys import maxint

def units_factory(subject, size, higher_unit=None,
        omissible=False, force_render=False):
    """
    A function that returns a function that will format a number with its
    units.

    Parameters:

    subject
        The name of the unit to be displayed
    size
        The size of this unit in relation to the base unit.
    higher_unit
        A function generated using this method that represents the next
        higher unit of measurement for this unit type.
    omissible
        Whether this output is omissible if the size is 0.
        Default is False.
    force_render
        Whether to forcibly render all units regardless of size.
        Default is False.
    """

    assert higher_unit is None or callable(higher_unit)

    def unit_method(value, omissible=omissible, with_remainder=False):
        if higher_unit:
            result, value = higher_unit(value, omissible=True,
                with_remainder=True)
            higher_size = higher_unit.size
        else:
            result = []
            higher_size = maxint

        remainder = value % higher_size
        derived = int(remainder / size)
        if (force_render or (value >= size and derived != 0) or
                not (omissible or result)):
            result.append((subject, derived))

        if with_remainder:
            return result, remainder
        return result

    unit_method.__name__ = subject
    unit_method.size = size
    return unit_method

def unit_number_tuple_to_str(values, plurals=None):
    if plurals is None:
        plurals = {}
    return ', '.join([('%d %s' % (v, v == 1 and s or plurals.get(s, s)))
        for s, v in values])


class UnitGroup(object):
    """
    Instances of this class is constructed using a list of definitions
    for a set of related, regular units (in decreasing order) and
    constructs an object with parameters with the name of the units,
    that when invoked, will return a human readable string down to that
    particular unit's size.

    See the accompanied units module for more examples.
    """

    def __init__(self, base_unit, ratios, plurals=None):
        self.base_unit = base_unit

        self.ratios = {}
        self.ratios.update(ratios)
        self.ratios[base_unit] = 1

        self.plurals = plurals or {}

        self.units = {}
        self.initialize()

    def initialize(self):
        self.units = {}
        build = sorted(self.ratios.items(), cmp=lambda x, y: cmp(y[1], x[1]))

        last = None
        for subject, size in build:
            plural = self.plurals.get(subject, subject)
            last = units_factory(subject, size=size, higher_unit=last)
            self.units[subject] = last
            self.units[plural] = last

    def respecify(self, ratios=None, plurals=None, keep_only=None, drop=None):
        """
        Returns a new UnitGroup object building up on this current one.

        ratios
            additional or updated ratios.
        plurals
            additional or updated plurals.
        keep_only
            a set of units to keep for the new object.
        omit
            a list of units to omit for the new object.
        """

        def newdict(*values):
            result = {}
            for v in values:
                if v:
                    result.update(v)
            return result

        new_ratios = newdict(self.ratios, ratios)
        new_plurals = newdict(self.plurals, plurals)

        if keep_only:
            keys = new_ratios.keys()
            for k in keys:
                if k not in keep_only:
                    new_ratios.pop(k, None)

        if drop:
            for d in drop:
                new_ratios.pop(d, None)

        return UnitGroup(self.base_unit, new_ratios, new_plurals)

    def as_attrs(self):
        return UnitGroupAttr(self)

    def __call__(self, *a, **kw):
        """
        Helper constructor for an instance of a value class.

        Normal arguments (non-keywords) are in this order:

        resolution

        Please refer to the base value class for the definitions of the
        above arguments.
        """

        args = list(reversed(a))
        resolution = args and args.pop() or self.base_unit
        # For now, just return the value in base units.
        value = 0
        for k, v in kw.iteritems():
            ratio = self.units.get(k, None)
            if ratio is None:
                raise TypeError("got an unexpected keyword argument '%s'" % k)
            value = value + self.ratios.get(k, 0) * v
        return UnitValue(self, value, resolution)


class UnitValue(object):

    def __init__(self, unit_group, value, resolution=None):
        # Assuming the UnitGroups are immutable.
        assert resolution in unit_group.units.keys()
        self.value = value
        self.unit_group = unit_group
        self.resolution = resolution

    def __str__(self):
        units = self.unit_group.units.get(self.resolution)
        values = units(self.value)
        return unit_number_tuple_to_str(values, self.unit_group.plurals)
