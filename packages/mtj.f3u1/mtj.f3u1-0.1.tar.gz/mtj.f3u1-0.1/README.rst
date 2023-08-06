Introduction
============

F3U1 - Factories and Functions for Fiddling with Units.

Backstory
---------

Once upon a time, the quest for a method to format seconds into a human
readable string was given to a hero.  Braving through the nets of Inter,
our hero stumbled upon place after places, such as State of Active, the
Exchange of Stacks, and even some other Hubs of Gits.  Some giants were
found, like Tens of Tens Lines Long of Repetition, others were touching
strange, unrelated things and looking complicated.  Those that spoke in
other unworldly incantations were of no use.  In the end, our hero gave
up, and constructed this monstrosity from the corpses of fairies::

    def format_timedelta(delta_t):
        hours = delta_t.seconds / 3600
        days = delta_t.days
        seconds = delta_t.seconds

        # Don't ask.  Read the test; be happy you don't have to write this.
        # (WTB something simple like str(delta_t) with more control.)
        # (Maybe I should just do this in javascript?)
        return '%(day)s%(hour)s' % {
            'day': days and '%(days)d day%(dayp)s%(comma)s' % {
                    'days': days,
                    'dayp': days != 1 and 's' or '',
                    'comma': seconds > 3599 and ', ' or '',
                } or '',
            'hour': (hours > 0 or days == 0 and hours == 0)
                and '%(hours)d hour%(hourp)s' % {
                    'hours': hours,
                    'hourp': hours != 1 and 's' or '',
                } or '',
        }

(OOC: It was actually tested; see earliest commits).

Then the realization hit our hero: sometimes a dworf want to micromanage
the resolution in minutes, and then the middle management dino will come
back and stamp on all the things and make the resolution to be no lesser
than a weeks in the name of opsec.  These arbitrary changes to this tiny
simple thing resulted in many gnashing of teeth and also many nightmares
that never seem to end.  Many cries of F7U12 was thrown about.

After countless nanoseconds of meditation, our hero destroyed 4 of those
F's and 11 of those U's towards the direction of the unseen horizon, the
solution was discovered, and it is one that transcends beyond time.

What?
=====

This resulted in the creation of original F3U1 - Factory For Formatting
Units.  Other descriptions used to fit, including Factory of Functions
for Formatting Units or Formatting Functions from Functions for Units.
However, over time as this module matured, it really became Factories
and Functions for Fiddling with Units.

While this started as a module for formatting time into a human friendly
string, this got generalized to be able to format arbitrary units, such
as non-metric measurements units, into a human readable string.  Then
this got further generalized into being callable objects that can be
used to construct an object representing some value and then be casted
into the same human readable string.

How?
====

Just install with pip in your virtualenv setup.

Alternatively you may clone this repository for running the tests, which
will require some other dependencies which are specified inside the
requirements.txt::

    $ git clone git://github.com/metatoaster/mtj.f3u1.git
    $ cd mtj.f3u1
    $ pip install -r requirements.txt
    $ python setup.py develop
