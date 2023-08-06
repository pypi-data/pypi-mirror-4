#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# file pyroots/brent.py
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
Brent's algorithm for root finding.

https://en.wikipedia.org/wiki/Brent%27s_method#Algorithm
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from pyroots.utils import EPS, Result, log_message, MESSAGES, ConvergenceError


#def brent_scipy(f, xa, xb, ftol=1e-6, max_iter=500, xtol=EPS, *args, **kwargs):
    #xpre = xa
    #xcur = xb

    ##check that the bracket's interval is sufficiently big.
    #if abs(xcur - xpre) < EPS:
        #return Result(None, None, 0, 0, False, "Initial bracket smaller than EPS.")

    ## check lower bound
    #fpre = f(xpre, *args, **kwargs)               # first function call
    #if abs(fpre) < ftol:
        #return Result(xpre, fpre, 0, 1, True, "Root is equal to the lower bracket")

    ## check upper bound
    #fcur = f(xcur, *args, **kwargs)               # second function call
    #if abs(fcur) < ftol:
        #return Result(xcur, fcur, 0, 2, True, "Root is equal to the upper bracket")

    ## check if the root is bracketed.
    #if fcur * fpre > 0.0:
        #return Result(None, None, 0, 2, False, "Root is not bracketed.")

    ##xblk, fblk = 0, 0
    ##spre, scur = 0, 0

    #for i in range(max_iter):
        #if (fpre * fcur) < 0:
            #xblk, fblk = xpre, fpre
            #spre = scur = xcur - xpre

        #if abs(fblk) < abs(fcur):
            #xpre, fpre = xcur, fcur
            #xcur, fcur = xblk, fblk
            #xblk, fblk = xpre, fpre

        ## Scipy's line 63.is missing.
        ##tol = xtol + rtol * fabs(xcur)

        #sbis = (xblk - xcur) / 2

        #if abs(fcur) < ftol:
            #return Result(xcur, fcur, i + 1, 2 + i, True, "Solution converged.")

        #if abs(sbis) < xtol:
            #return Result(xcur, fcur, i + 1, 2 + i, False, "Precision not achieved. Bracket too small.")

        ##if (fcur == 0 or abs(sbis) < tol):
            ##return xcur

        #if abs(spre) > xtol and abs(fcur) < abs(fpre):
            #if xpre == xblk:
                ## interpolate
                #stry = -fcur * (xcur - xpre) / (fcur - fpre)
            #else:
                ## extrapolate
                #dpre = (fpre - fcur) / (xpre - xcur)
                #dblk = (fblk - fcur) / (xblk - xcur)
                #stry = -fcur * (fblk * dblk - fpre * dpre) / (dblk * dpre * (fblk - fpre))
            #if ((2 * abs(stry)) < min(abs(spre), 3 * abs(sbis) - xtol)):
                ## good short step
                #spre, scur = scur, stry
            #else:
                ##bisect
                #spre, scur = sbis, sbis
        #else:
            ## bisect
            #spre, scur = sbis, sbis

        #xpre, fpre = xcur, fcur
        #if (abs(scur) > xtol):
            #xcur += scur
        #else:
            #xcur += xtol if sbis > 0 else -xtol

        #fcur = f(xcur, *args, **kwargs)

    #return Result(xcur, fcur, i + 1, 3 + i, False, "exceeded allowed iterations.")


def brent(f, xa, xb, *args, ftol=1e-6, xtol=EPS, max_iter=500, raise_on_fail=True, **kwargs):
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
    fa = f(xa, *args, **kwargs)               # first function call
    if abs(fa) < ftol:
        return Result(xa, fa, 0, 1, True, MESSAGES["lower bracket"])

    # check upper bound
    fb = f(xb, *args, **kwargs)               # second function call
    if abs(fb) < ftol:
        return Result(xb, fb, 0, 2, True, MESSAGES["upper bracket"])

    # check if the root is bracketed.
    if fa * fb > 0.0:
        if raise_on_fail:
            raise ConvergenceError(MESSAGES["no bracket"])
        else:
            return Result(None, None, 0, 2, False, MESSAGES["no bracket"])

    #xblk, fblk = 0, 0
    #spre, scur = 0, 0

    for i in range(max_iter):
        if (fa * fb) < 0:
            xblk, fblk = xa, fa
            spre = scur = xb - xa

        if abs(fblk) < abs(fb):
            xa, fa = xb, fb
            xb, fb = xblk, fblk
            xblk, fblk = xa, fa

        # Scipy's line 63.is missing.
        #tol = xtol + rtol * fabs(xb)

        sbis = (xblk - xb) / 2

        if abs(fb) < ftol:
            return Result(xb, fb, i + 1, 2 + i, True, MESSAGES["convergence"])

        if abs(sbis) < xtol:
            if raise_on_fail:
                raise ConvergenceError(MESSAGES["small bracket"])
            else:
                return Result(xb, fb, i + 1, 2 + i, False, MESSAGES["small bracket"])

        #if (fb == 0 or abs(sbis) < tol):
            #return xb

        if abs(spre) > xtol and abs(fb) < abs(fa):
            if xa == xblk:
                # interpolate
                stry = -fb * (xb - xa) / (fb - fa)
            else:
                # extrapolate
                dpre = (fa - fb) / (xa - xb)
                dblk = (fblk - fb) / (xblk - xb)
                stry = -fb * (fblk * dblk - fa * dpre) / (dblk * dpre * (fblk - fa))
            if ((2 * abs(stry)) < min(abs(spre), 3 * abs(sbis) - xtol)):
                # good short step
                spre, scur = scur, stry
            else:
                #bisect
                spre, scur = sbis, sbis
        else:
            # bisect
            spre, scur = sbis, sbis

        xa, fa = xb, fb
        if (abs(scur) > xtol):
            xb += scur
        else:
            xb += xtol if sbis > 0 else -xtol

        fb = f(xb, *args, **kwargs)

    if raise_on_fail:
        raise ConvergenceError(MESSAGES["iterations"])
    else:
        return Result(xb, fb, i + 1, 3 + i, False, MESSAGES["iterations"])


def brentw(f, xa, xb, *args, ftol=1e-6, xtol=EPS, max_iter=500, raise_on_fail=True, **kwargs):
    """
    Brent Method, following Wikipedia's article algorithm.
    """
    #check that the bracket's interval is sufficiently big.
    if abs(xb - xa) < EPS:
        return Result(None, None, 0, 0, False, "Initial bracket smaller than EPS.")

    # check lower bound
    fa = f(xa, *args, **kwargs)               # first function call
    if abs(fa) < ftol:
        return Result(xa, fa, 0, 1, True, "Root is equal to the lower bracket")

    # check upper bound
    fb = f(xb, *args, **kwargs)               # second function call
    if abs(fb) < ftol:
        return Result(xb, fb, 0, 2, True, "Root is equal to the upper bracket")

    # check if the root is bracketed.
    if fa * fb > 0.0:
        return Result(None, None, 0, 2, False, "Root is not bracketed.")

    if abs(fa) < abs(fb):
        xa, xb = xb, xa
        fa, fb = fb, fa

    xc, fc = xa, fa
    mflag = True

    for i in range(max_iter):
        # try to calculate `xs` by using inverse quadratic interpolation
        # if you can't use the secant rule.
        if fa != fc and fb != fc:
            xs = (xa * fb * fc / ((fa - fb) * (fa - fc)) +
                 xb * fa * fc / ((fb - fa) * (fb - fc)) +
                 xc * fa * fb / ((fc - fa) * (fc - fb)))
        else:
            xs = xb - fb * (xb - xa) / (fb - fa)

        # check if the value of `xs` is acceptable.
        # if it isn't use bisection.
        if ((xs < ((3 * xa + xb) / 4) or xs > xb) or
            (mflag == True  and (abs(xs - xb)) >= (abs(xb - xc) / 2)) or
            (mflag == False and (abs(xs - xb)) >= (abs(xc - d) / 2)) or
            (mflag == True  and (abs(xb - xc)) < EPS) or
            (mflag == False and (abs(xc - d)) < EPS)):

            xs = (xa + xb) / 2
            mflag = True
        else:
            mflag = False

        fs = f(xs, *args, **kwargs)

        if abs(fs) < ftol:
            return Result(xs, fs, i + 1, 3 + i, True, MESSAGES["small bracket"])

        if abs(xb - xa) < xtol:
            return Result(xs, fs, i + 1, 3 + i, False, MESSAGES["small bracket"])

        d = xc
        xc, fc = xb, fb
        if fa * fs < 0:
            xb, fb = xs, fs
        else:
            xa, fa = xs, fs

        if abs(fa) < abs(fb):
            xa, xb = xb, xa
            fa, fb = fb, fa

    return Result(xs, fs, i + 1, 3 + i, False, MESSAGES["iterations"])
