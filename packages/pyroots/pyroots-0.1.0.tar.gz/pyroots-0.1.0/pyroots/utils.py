#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# file pyroots/wrappers.py
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
pyroots/utils.py
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys


class Result(object):
    def __init__(self, x0, fx0, iterations, func_evaluations, convergence, msg=""):
        self.x0 = x0
        self.fx0 = fx0
        self.iterations = iterations
        self.func_calls = func_evaluations
        self.convergence = convergence
        self.msg = msg

    def __repr__(self):
        # By convention, when there is no convergence, we return `None` for
        # `x0` and `f(x0)`. None does not work well with format specifier `f`.
        representation = "iter={iterations:3d}, "
        representation += "func_calls={func_calls:3d}, "
        representation += "convergence={convergence}, "
        representation += "x0={x0:.16f}, " if self.x0 is not None else "x0=None, "
        representation += "f(x0)={fx0: .1e}, " if self.x0 is not None else "f(x0)=None, "
        representation += "msg={msg}"

        return representation.format(**self.__dict__)



MESSAGES = {
    "small bracket": "Bracket is smaller than tolerance.",
    "lower bracket": "Root is equal to the lower bracket",
    "upper bracket": "Root is equal to the upper bracket",
    "no bracket": "Root is not bracketed.",
    "convergence": "Solution converged.",
    "iterations": "Exceeded max iterations."}


EPS = sys.float_info.epsilon
log_message = "Iteration {i:3d}, x=[{a: .15f}, {b: .15f}], Δx={dx: .15f}, f=[{fa: .15f}, {fb: .15f}]"


class ConvergenceError(Exception):
    pass
