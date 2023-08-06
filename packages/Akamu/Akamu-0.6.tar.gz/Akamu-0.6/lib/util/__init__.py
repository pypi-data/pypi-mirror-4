#!/usr/bin/env python
## From http://code.activestate.com/recipes/578294/ (r1)

def enum(*sequential, **named):
    # Check for duplicate keys
    names = list(sequential)
    names.extend(named.keys())
    if len(set(names)) != len(names):
        raise KeyError('Cannot create enumeration with duplicate keys!')

    # Build property dict
    enums = dict(zip(sequential, range(len(sequential))), **named)
    if not enums:
        raise KeyError('Cannot create empty enumeration')

    if len(set(enums.values())) < len(enums):
        raise ValueError('Cannot create enumeration with duplicate values!')

    # Function to be called as fset/fdel
    def err_func(*args, **kwargs):
        raise AttributeError('Enumeration is immutable!')

    # function to be called as fget
    def getter(cls, val):
        return lambda cls: val

    # Create a base type
    t = type('enum', (object,), {})

    # Add properties to class by duck-punching
    for attr, val in enums.iteritems():
        setattr(t, attr, property(getter(t, val), err_func, err_func))

    # Return an instance of the new class
    return t()