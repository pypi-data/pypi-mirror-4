#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# file pyroots/ridder.py
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
Ridder's algorithm for root finding.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from math import sqrt
from pyroots.utils import EPS, Result, MESSAGES, ConvergenceError

def ridder(f, xa, xb, *args, ftol=1e-6, xtol=EPS, max_iter=500, raise_on_fail=True, **kwargs):
    """
    Solves `f(x) = 0` in interval `[a, b]` using Ridder's Method.

    `f` must be solvable in `[a, b]`. Also `f(a)` and `f(b)` must have different
    signs.

    Parameters
    ----------
    f : function
        The function whose root we are searching.
        `f` must take at least one argument.
    xa : float
        The lower bound of the bracket.
    xb : float
        The upper bound of the bracket.
    ftol : float
        The required accuracy for `f`.
    xtol : float
        TODO
    max_iter: integer
        The maximum allowed number of iterations.
    *args: tuple
        Function's `f` arguments. If f takes only one argument, then this is an
        empty tuple.

    Returns
    -------
    result: `Result`'s instance.

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

    # begin iterations
    for i in range(max_iter):

        # Bisect the bracket and check if convergence has been achieved
        xm = 0.5 * (xa + xb)
        fm = f(xm, *args, **kwargs)

        if abs(fm) < ftol:
            return Result(xm, fm, i + 1, 3 + 2 * i, True, MESSAGES["convergence"])

        # `t` is the denominator followingly
        # if `t == 0` then the ridder's method cannot be applied due to a
        # ZeroDivisionError. Not sure when this can happen though...
        # Perhaps on an almost vertical line.
        # TODO write a test for this case.
        # NOTE 1: Scipy's ridder method doesn't check for t == 0.
        # NOTE 2: `t` is always positive, so we do not need a try/except block
        #         to check if the value is positive.
        t = sqrt(fm ** 2 - fa * fb)
        if t == 0.0:
            return Result(xm, fm, i + 1, 3 + 2 * i, False, "Solution is not possible.")

        # calculate the improved x from Ridder's formula and
        # NOTE: Scipy's version is a little bit different. Didn't find any
        # reference though.
        sign = -1 if fa < fb else 1
        xs = xm + (xm - xa) * sign * fm / t
        fs = f(xs, *args, **kwargs)

        if abs(fs) < ftol:
            return Result(xs, fs, i + 1, 3 + i, True, MESSAGES["convergence"])

        # When ftol is very small (e.g. 1e-15) then there are cases that the
        # method can't converge in a reasonable amount of iterations.
        # One such case is f(x) = 24.5 * x**5 - 92.2 * x**3 + 23 * x - 12
        # In order to prevent the method from becoming stagnant we keep record
        # of the old values of xm and xs and we check if they change values
        # during the iterations.
        # NOTE: Perhaps this check is not very robust.
        #if i > 0:
            #if abs(xs - xs_old) < xtol and abs(xm - xm_old) < xtol:
                #return Result(xs, fs, i + 1, 4 + 2 * i, False,
                              #"Precision not achieved. Iteration stagnant.")

        # check for the new bracket size.
        #print(abs(max(xa, xb)) * xtol)
        #if abs(xb - xa) < abs(max(xa, xb)) * xtol:
        if abs(xb - xa) < xtol:
            if raise_on_fail:
                raise ConvergenceError(MESSAGES["small bracket"])
            else:
                return Result(xs, fs, i + 1, 3 + i, False, MESSAGES["small bracket"])

        # Re-bracket the root as tightly as possible
        if fm * fs > 0.0:
            if fa * fs < 0.0:
                xb, fb = xs, fs
            else:
                xa, fa = xs, fs
        else:
            xa, fa = xm, fm
            xb, fb = xs, fs

        # Ensure that xa < xb
        # NOTE: This is not necessary but it is useful for debugging.
        if xa > xb:
            xa, xb = xb, xa
            fa, fb = fb, fa

        # Store values of the previous iteration.
        xm_old = xm
        xs_old = xs

    # If max_iter equals 0 then an exception is thrown because
    # xm and fm have not been defined.
    if raise_on_fail:
        raise ConvergenceError(MESSAGES["iterations"])
    else:
        return Result(xs, fs, i + 1, 3 + i, False, MESSAGES["iterations"])
