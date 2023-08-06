Rafutils
========

A few helpful utilities that I find useful.


Autovivification
----------------

Dictionary type that allows for dynamic allocation of nested key values
without prior defintion. ::

    >>> a = AutoVivification()
    >>> a[1][2] = 3

Multiprocessing Wrapper
-----------------------

This module provides a set of methods for handling multi-threading
patterns more easily. ::

    >>> import user_metrics.utils.multiprocessing_wrapper as mpw
    >>> mpw.build_thread_pool(['one','two'],len,2,[])
    [2,2]

Record Type
-----------

Defines the recordtype method which returns a type definition object
that allows for the creation of mutable objects with specified
attributes.  These are essentially identical to collections.namedtuple
except that the attributes may be changed after the namedtuple objects are
created. ::

    >>> Point = recordtype('Point', 'x y', default=0)
    >>> Point()                 # instantiate with defaults
    Point(x=0, y=0)


Miscellaneous
-------------

Some miscellaneous methods exposed by this package.

Format Timestamp
----------------

The ``format_timestamp`` method takes a timestamp representation (string
or datetime) and convert to a standard string representation.

Enumeration
------------

The ``enum`` method implements an enumeration::

    >>> Numbers = enum('ZERO', 'ONE', 'TWO')
    >>> Numbers.ZERO
    0
    >>> Numbers.ONE
    1

Build Named Tuple
-----------------

Given a set of types, values, and names builds a named tuple.  This
method expects three lists all of the same length and returns a
dynamically built namedtuple object.  Currently, only ``list``,
``str``, ``int``, and ``float`` cast methods are accepted as members
of ``types``.  The mothod is named ``build_namedtuple``.


Unpack Fields
-------------

Unpacks the attributes and values of a record type or named tuple into
an ordered dictionary.
