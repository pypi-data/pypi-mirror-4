#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# file pyroots/bisect.py
#
#############################################################################
# Copyright (c) 2013 by Panagiotis Mavrogiorgos
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name(s) of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AS IS AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#############################################################################
#
# @license: http://opensource.org/licenses/BSD-3-Clause
# @authors: see AUTHORS.txt

"""
bisect method.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from math import copysign
from pyroots.utils import EPS, Result, MESSAGES, ConvergenceError


def bisect(f, xa, xb, *args, ftol=1e-6, xtol=EPS, max_iter=500, raise_on_fail=True, **kwargs):
    """
    Solves `f(x) = 0` in interval `[xa, xb]` using Bisection Method.

    Function `f` must be solvable in `[xa, xb]`. Also `f(xa)` and `f(xb)` must
    have different signs.

    Parameters
    ----------
    :param function f:
        A single-variable function that we are searching for it's root within
        the given interval. It must take at least one argument and any number
        of positional or keyword arguments.
    :param float xa:
        The lower bound of the interval.
    :param float xb:
        The upper bound of the interval.
    :param tuple *args:
        Function's `f` positional arguments.
    :param float ftol:
        The required accuracy for `f`.
    :param float xtol:
        Equals machine accuracy.
    :param int max_inter:
        The maximum allowed number of iterations.
    :param dict kwargs:
        Function's `f` keyword arguments.

    Returns
    -------
    :returns: `Result`'s instance.

    :raises: `ConvergenceError` if `raise_on_fail` is True and the function fails to
        converge. If `raise_on_fail` is `False` then it returns a `Result` instance.

    """
    # sanity check
    if xtol < EPS:
        raise ArithmeticError("xtol can't be lower than EPS (xtol=%.15f, EPS=%.15f)" % (xtol, EPS))
    if ftol < EPS:
        raise ArithmeticError("ftol can't be lower than EPS (ftol=%.15f, EPS=%.15f)" % (ftol, EPS))

    #check that the bracket's interval is sufficiently big.
    if abs(xb - xa) < xtol:
        if raise_on_fail:
            raise ConvergenceError(MESSAGES["small bracket"])
        else:
            return Result(None, None, 0, 0, False, MESSAGES["small bracket"])

    # check lower bound
    fa = f(xa, *args, **kwargs)               # First function call
    if abs(fa) < ftol:
        return Result(xa, fa, 0, 1, True, MESSAGES["lower bracket"])

    # check upper bound
    fb = f(xb, *args, **kwargs)               # Second function call
    if abs(fb) < ftol:
        return Result(xb, fb, 0, 2, True, MESSAGES["upper bracket"])

    # check if the root is bracketed.
    if fa * fb > 0.0:
        if raise_on_fail:
            raise ConvergenceError(MESSAGES["no bracket"])
        else:
            return Result(None, None, 0, 2, False, MESSAGES["no bracket"])

    # Bisect the bracket and calculate the new function value.
    for i in range(max_iter):
        xm = 0.5 * (xa + xb)
        fm = f(xm, *args, **kwargs)           # New function call.

        # check for convergence.
        if abs(fm) < ftol:
            return Result(xm, fm, i + 1, 3 + i, True, MESSAGES["convergence"])

        # close the bracket
        if copysign(1, fm) == copysign(1, fa):
            xa = xm
            fa = fm
        else:
            xb = xm
            fb = fm

        # check for the new bracket size.
        #print(abs(max(xa, xb)) * xtol)
        #if abs(xb - xa) < abs(max(xa, xb)) * xtol:
        if abs(xb - xa) < xtol:
            if raise_on_fail:
                raise ConvergenceError(MESSAGES["small bracket"])
            else:
                return Result(xm, fm, i + 1, 3 + i, False, MESSAGES["small bracket"])

    # If max_iter equals 0 then an exception is thrown because
    # xm and fm have not been defined.
    if raise_on_fail:
        raise ConvergenceError(MESSAGES["iterations"])
    else:
        return Result(xm, fm, i + 1, 3 + i, False, MESSAGES["iterations"])
