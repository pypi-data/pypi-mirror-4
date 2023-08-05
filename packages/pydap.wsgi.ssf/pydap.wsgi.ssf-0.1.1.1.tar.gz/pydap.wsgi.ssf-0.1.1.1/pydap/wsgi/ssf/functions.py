"""
Server-side functions.

From the DAP 2.0 specification:

    4.1.3 Server Functions
    A constraint expression MAY also use functions executed by the server. These can appear in a selection or in a
    projection, although there are restrictions about the data types functions can return.

    A function which appears in the projection clause MAY return any of the DAP data types. In this case the return
    value of the function is treated as if it is a variable present in the top level of the Dataset (see Section 3.3.2 on
    page 10).

    A function which appears in the selection clause MAY return any atomic type if it is used in one of the relational
    sub-expressions. If a function in the selection clause is used as the entire sub-expression, it MUST return an
    integer value. If that value is zero, the function will evaluate as boolean false, otherwise it will evaluate as
    boolean true.

    When functions encounter an error, a DAP server MUST signal that condition by returning an error response.
    A server MAY NOT return a partial response; any error encountered while evaluating the constraint expression
    MUST result in a response that contains an unambiguous error message.

    6.1.1.3 Calling server-side functions Functions MAY be called as part of either the projection or selection
    clauses. In the case of a selection, the function MUST return a value which can be used when evaluating the
    clause. In the case of a projection, the function MUST return a DAP variable which will then be the return
    value of the request or it MUST return nothing in which case it is run for side effect only.

        selection = *relation | *function
        relation = (id rel-op id) | (value rel-op id) | (id rel-op value)
        value = constant | ( "{" 1#constant "}" )
        constant = quoted-string | <int> | <float> | URL

Here's some quick rules for implementing functions in Pydap:

1. Functions always receive the dataset as the first argument. Additional arguments come from the function signature.
   For example, a function called as ``foo(bar, 1)`` will be called on the Python side as ``foo(dataset, bar, 1)``,
   with ``bar`` being a variable.

2. Functions that work on the selection always return a Sequence. They also should act on Sequences.

3. Functions thar work on Sequences called on the projection will also return a new Sequence, with the same name as 
   the original one. For example, calling ``?density(seq.t, seq.s, seq.p)`` will return a Sequence with name ``seq``
   with a variable ``density`` on it.

"""

from datetime import datetime
import re

import numpy as np

from coards import to_udunits

from pydap.lib import walk
from pydap.exceptions import ConstraintExpressionError
from pydap.model import *
from pydap.handlers.helper import parse_selection


def bounds(dataset, xmin, xmax, ymin, ymax, zmin, zmax, tmin, tmax):
    """
    Version 1.0

    This function is used by GrADS to access Sequences, eg:

        http://server.example.com/dataset.dods?sequence&bounds(0,360,-90,90,500,500,00Z01JAN1970,00Z01JAN1970)

    We assume the dataset has only a single Sequence.

    """
    # find sequence
    for sequence in walk(dataset, SequenceType):
        break  # get first sequence
    else:
        raise ConstraintExpressionError('Function "bounds" should be used on a Sequence.')

    sequence.data = list(sequence.data)  # consume generators 
    valid = np.ones(len(sequence.data), np.int)

    for i, name in enumerate(sequence.keys()):
        child = sequence[name]
        if child.attributes.get('axis', '').lower() == 'x':
            valid = valid & [ xmin <= row[i] <= xmax for row in sequence.data ]
        elif child.attributes.get('axis', '').lower() == 'y':
            valid = valid & [ ymin <= row[i] <= ymax for row in sequence.data ]
        elif child.attributes.get('axis', '').lower() == 'z':
            valid = valid & [ zmin <= row[i] <= zmax for row in sequence.data ]
        elif child.attributes.get('axis', '').lower() == 't':
            tmin = to_udunits(datetime.strptime(tmin, '%HZ%d%b%Y'), child.units)
            tmax = to_udunits(datetime.strptime(tmax, '%HZ%d%b%Y'), child.units)
            valid = valid & [ tmin <= row[i] <= tmax for row in sequence.data ]

    out = SequenceType(name=sequence.name)
    out['bounds'] = BaseType(name='bounds', data=valid)
    return out


def geogrid(dataset, var, top, left, bottom, right, expressions=None):
    """
    Version 1.1

    http://docs.opendap.org/index.php/Server_Side_Processing_Functions#geogrid

    """
    if expressions is None:
        expressions = []

    # build a slice that contains all data, and change it according to the
    # bounding box values
    slice_ = [slice(None) for dim in var.dimensions]
    wrap = False
    for i, dim in enumerate(var.dimensions):
        axis = dataset[dim]
        if getattr(axis, 'axis', '').lower() == 'x':
            axis = np.asarray(axis)
            i0 = np.searchsorted(axis[:], left, 'right') - 1
            i1 = np.searchsorted(axis[:], right, 'left') + 1
            if i0 < i1:
                slice_[i] = slice(i0, i1, 1)
            else:
                wrap = True
                j, lon = i, dim
                slice1 = slice(i0, None, 1)
                slice2 = slice(None, i1, 1)
        elif getattr(axis, 'axis', '').lower() == 'y':
            axis = np.asarray(axis)
            if axis[1] > axis[0]:
                j0 = np.searchsorted(axis[:], bottom, 'right') - 1
                j1 = np.searchsorted(axis[:], top, 'left') + 1
                slice_[i] = slice(j0, j1, 1)
            else:
                j0 = np.searchsorted(axis[:][::-1], bottom, 'right') - 1
                j1 = np.searchsorted(axis[:][::-1], top, 'left') + 1
                slice_[i] = slice(-j1, -j0, 1)

    # apply slice
    var = var[tuple(slice_)]

    # now do the same with expressions
    for expression in expressions:
        for new_slice in parse_expr(expression, var):
            var = var[new_slice]

    if wrap:
        # apply a new slice, along lon only, and concatenate
        grid1 = var[tuple( [slice(None)]*j + [slice1] )]
        grid2 = var[tuple( [slice(None)]*j + [slice2] )]
        var.array.data = np.concatenate((grid1.array[:], grid2.array[:]), j)
        var.array.shape = var.array.data.shape
        var.maps[lon].data = np.concatenate((grid1.maps[lon][:], grid2.maps[lon][:]), 0)
        var.maps[lon].shape = var.maps[lon].data.shape

    return var


def parse_expr(expression, dataset):
    RELOP = r"(<=|<|>=|>|=|!=)"
    tokens = re.split(RELOP, expression)
    if len(tokens) == 5:
        exprs = [ ''.join(tokens[2::-1]), ''.join(tokens[2:]) ]  # order as [var relop const]
    elif len(tokens) == 3:
        exprs = [ ''.join(tokens) ]
    else:
        raise ConstraintExpressionError("Invalid expression: %s" % expression)

    for expr in exprs:
        var, op, const = parse_selection(expr, dataset)
        yield op(var, const)


def mean(dataset, var, axis=0):
    """
    Version 1.0

    Calculates the mean of an array along a given axis.

    """
    axis = int(axis)
    if isinstance(var, BaseType):
        var.data = np.mean(var.data[:], axis=axis)
        var.shape = var.data.shape
    elif isinstance(var, GridType):
        var.array.data = np.mean(var.array.data[:], axis=axis)
        var.array.dimensions = tuple(dim for i,dim in enumerate(var.dimensions) if i != axis)
        var.shape = var.array.shape = var.array.data.shape
        del var[ var.dimensions[axis] ]
    return var
