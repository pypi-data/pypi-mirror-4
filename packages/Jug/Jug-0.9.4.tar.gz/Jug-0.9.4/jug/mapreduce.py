# -*- coding: utf-8 -*-
# Copyright (C) 2008-2013, Luis Pedro Coelho <luis@luispedro.org>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License : MIT

'''
mapreduce: Build tasks that follow a map-reduce pattern.
'''

from __future__ import division
from jug import Task
from .utils import identity
from .hash import hash_one

from itertools import chain
import operator

__all__ = [
    'mapreduce',
    'map',
    'reduce',
    ]

def _get_function(f):
    if getattr(f, '_jug_is_task_generator', False):
        hvalue = hash_one(f)
        f = f.f
        f.__jug_hash__ = lambda: hvalue
        return f
    return f

def _jug_map_reduce(reducer, mapper, inputs):
    import __builtin__
    reducer = _get_function(reducer)
    mapper = _get_function(mapper)
    return __builtin__.reduce(reducer, __builtin__.map(mapper, inputs))
def _jug_reduce(reducer, inputs):
    import __builtin__
    reducer = _get_function(reducer)
    return __builtin__.reduce(reducer, chain(inputs))

def _break_up(lst, step):
    start = 0
    next = step
    while start < len(lst):
        yield lst[start:next]
        start = next
        next += step


def _jug_map(mapper, es):
    import __builtin__
    return __builtin__.map(mapper, es)

def _jug_map_curry(mapper, es):
    return [mapper(*e) for e in es]


def mapreduce(reducer, mapper, inputs, map_step=4, reduce_step=8):
    '''
    task = mapreduce(reducer, mapper, inputs, map_step=4, reduce_step=8)

    Create a task that does roughly the following::

        reduce(reducer, map(mapper, inputs))

    Roughly because the order of operations might be different. In particular,
    `reducer` should be a true `reducer` functions (i.e., commutative and
    associative).

    Parameters
    ----------
    reducer : associative, commutative function
            This should map
                  Y_0,Y_1 -> Y'
    mapper : function from X -> Y
    inputs : list of X

    map_step : integer, optional
            Number of mapping operations to do in one go.
            This is what defines an inner task. (default: 4)
    reduce_step : integer, optional
            Number of reduce operations to do in one go.
            (default: 8)

    Returns
    -------
    task : jug.Task object
    '''
    reducers = [Task(_jug_map_reduce, reducer, mapper, input_i) for input_i in _break_up(inputs, map_step)]
    while len(reducers) > 1:
        reducers = [Task(_jug_reduce, reducer, reduce_i) for reduce_i in _break_up(reducers, reduce_step)]
    if len(reducers) == 0:
        return identity([])
    elif len(reducers) == 1:
        return reducers[0]
    else:
        assert False, 'This is a bug'

def map(mapper, sequence, map_step=4):
    '''
    sequence' = map(mapper, sequence, map_step=4)

    Roughly equivalent to::

        sequence' = [Task(mapper,s) for s in sequence]

    except that the tasks are grouped in groups of `map_step`

    Parameters
    ----------
    mapper : function
        function from A -> B
    sequence : list of A
    map_step : integer, optional
        nr of elements to process per task. This should be set so that each
        task takes the right amount of time.

    Returns
    -------
    sequence' : list of B
        sequence'[i] = mapper(sequence[i])

    See Also
    --------
    mapreduce
    currymap: function
        Curried version of this function
    '''
    if map_step == 1:
        return [Task(mapper, s) for s in sequence]
    result = []
    for ss in _break_up(sequence, map_step):
        t = Task(_jug_map, _get_function(mapper), ss)
        for i,_ in enumerate(ss):
            result.append(t[i])
    return result

def currymap(mapper, sequence, map_step=4):
    '''
    sequence' = currymap(mapper, sequence, map_step=4)

    Roughly equivalent to::

        sequence' = [Task(mapper,*s) for s in sequence]

    except that the tasks are grouped in groups of `map_step`

    Parameters
    ----------
    mapper : function
        function from A1 -> A2 ... -> An -> B
    sequence : list of (A1,A2,...,An)
    map_step : integer, optional
        nr of elements to process per task. This should be set so that each
        task takes the right amount of time.

    Returns
    -------
    sequence' : list of B
        sequence'[i] = mapper(*sequence[i])

    See Also
    --------
    mapreduce: function
    map: function
        Uncurried version of this function
    '''
    if map_step == 1:
        return [Task(mapper, *s) for s in sequence]
    result = []
    for ss in _break_up(sequence, map_step):
        t = Task(_jug_map_curry, _get_function(mapper), ss)
        for i,_ in enumerate(ss):
            result.append(t[i])
    return result




def reduce(reducer, inputs, reduce_step=8):
    '''
    task = reduce(reducer, inputs, reduce_step=8)

    Parameters
    ----------
    reducer : associative, commutative function
            This should map
                  Y_0,Y_1 -> Y'
    inputs : list of X
    reduce_step : integer, optional
            Number of reduce operations to do in one go.
            (default: 8)

    Returns
    -------
    task : jug.Task object

    See Also
    --------
    mapreduce
    '''
    return mapreduce(reducer, None, inputs, reduce_step=reduce_step)

