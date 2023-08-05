#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Noah Watkins <noah@noahdesu.com>
# Copyright 2011 Yesudeep Mangalapilly <yesudeep@gmail.com>
# Copyright 2012 Google Inc. All Rights Reserved.
#
# MIT License
# -----------
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT  OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

""":synopsis: ctypes-based GMP wrapper.
:module: mom.gmp
:see: http://noahdesu.com/2009/12/14/python-gmp/

.. autoclass:: Integer
.. autoclass:: Float
.. autoclass:: Rational
.. autoclass:: Random
"""


from __future__ import absolute_import

import ctypes

from ctypes import util
from mom import _compat


__author__ = "yesudeep@google.com (Yesudeep Mangalapilly)"


# pylint: disable-msg=W0212
# pylint: disable-msg=C0103

if _compat.HAVE_PYTHON3:

  def number_to_pybytes(num):
    """
    Converts number to bytes.
    """
    return str(num).encode("latin1")

  def to_str(raw_bytes_num):
    """
    Converts bytes to the appropriate string representation for the Python
    version.
    """
    #return raw_bytes_num.decode("latin1")
    return str(raw_bytes_num, "latin1")
else:

  def number_to_pybytes(num):
    """
    Converts number to bytes.
    """
    return str(num)

  def to_str(raw_bytes_num):
    """
    Converts bytes to the appropriate string representation for the Python
    version.
    """
    return raw_bytes_num


# Find the GMP library
_libgmp_path = util.find_library("gmp")
if not _libgmp_path:
  raise ImportError("Unable to find libgmp")
  # raise EnvironmentError("Unable to find libgmp")
_libgmp = ctypes.CDLL(_libgmp_path)


# GNU MP structures
#
#  - TODO: choose between different definitions of these structures based on
#  checking library/arch. For example, different library configuration options
#  and 32-bit/64-bit systems.
#
class c_mpz_struct(ctypes.Structure):
  """Internal structure."""
  _fields_ = [
      ("_mp_alloc", ctypes.c_int),
      ("_mp_size", ctypes.c_int),
      ("_mp_d", ctypes.POINTER(ctypes.c_ulonglong))]


class c_gmp_randstate_struct(ctypes.Structure):
  """Internal structure."""
  _fields_ = [
      ("_mp_seed", c_mpz_struct),
      ("_mp_alg", ctypes.c_int),
      ("_mp_algdata", ctypes.c_voidp)]


class c_mpq_struct(ctypes.Structure):
  """Internal structure."""
  _fields_ = [
      ("_mp_num", c_mpz_struct),
      ("_mp_den", c_mpz_struct)]


class c_mpf_struct(ctypes.Structure):
  """Internal structure."""
  _fields_ = [
      ("_mp_prec", ctypes.c_int),
      ("_mp_size", ctypes.c_int),
      ("_mp_exp", ctypes.c_long),
      ("_mp_d", ctypes.POINTER(ctypes.c_long))]

#------------------------------------------------------------------------------
# Function references into MP library
#------------------------------------------------------------------------------

# Gnu MP integer routines
_MPZ_init = _libgmp.__gmpz_init
_MPZ_clear = _libgmp.__gmpz_clear
_MPZ_add = _libgmp.__gmpz_add
_MPZ_sub = _libgmp.__gmpz_sub
_MPZ_mul = _libgmp.__gmpz_mul
_MPZ_div = _libgmp.__gmpz_tdiv_q
_MPZ_fdiv = _libgmp.__gmpz_fdiv_q
_MPZ_fmod = _libgmp.__gmpz_fdiv_r
_MPZ_fdivmod = _libgmp.__gmpz_fdiv_qr
_MPZ_mod = _libgmp.__gmpz_mod
_MPZ_and = _libgmp.__gmpz_and
_MPZ_ior = _libgmp.__gmpz_ior
_MPZ_xor = _libgmp.__gmpz_xor
_MPZ_abs = _libgmp.__gmpz_abs
_MPZ_neg = _libgmp.__gmpz_neg
_MPZ_cmp = _libgmp.__gmpz_cmp
_MPZ_set_str = _libgmp.__gmpz_set_str
_MPZ_get_str = _libgmp.__gmpz_get_str
_MPZ_urandomb = _libgmp.__gmpz_urandomb
_MPZ_urandomm = _libgmp.__gmpz_urandomm
_MPZ_rrandomb = _libgmp.__gmpz_rrandomb

# Gnu MP floating point routines
_MPF_set_default_prec = _libgmp.__gmpf_set_default_prec
_MPF_init = _libgmp.__gmpf_init
_MPF_clear = _libgmp.__gmpf_clear
_MPF_add = _libgmp.__gmpf_add
_MPF_sub = _libgmp.__gmpf_sub
_MPF_mul = _libgmp.__gmpf_mul
_MPF_div = _libgmp.__gmpf_div
_MPF_abs = _libgmp.__gmpf_abs
_MPF_neg = _libgmp.__gmpf_neg
_MPF_cmp = _libgmp.__gmpf_cmp
_MPF_eq = _libgmp.__gmpf_eq
_MPF_set_str = _libgmp.__gmpf_set_str
_MPF_get_str = _libgmp.__gmpf_get_str


# Gnu MP random generator routines
_GMP_randinit_default = _libgmp.__gmp_randinit_default
_GMP_randinit_mt = _libgmp.__gmp_randinit_mt
_GMP_randclear = _libgmp.__gmp_randclear
_GMP_randseed = _libgmp.__gmp_randseed
_GMP_urandomm = _libgmp.__gmpz_urandomm

# Gnu MP rational number routines
_MPQ_init = _libgmp.__gmpq_init
_MPQ_clear = _libgmp.__gmpq_clear
_MPQ_add = _libgmp.__gmpq_add
_MPQ_sub = _libgmp.__gmpq_sub
_MPQ_mul = _libgmp.__gmpq_mul
_MPQ_div = _libgmp.__gmpq_div
_MPQ_abs = _libgmp.__gmpq_abs
_MPQ_neg = _libgmp.__gmpq_neg
_MPQ_cmp = _libgmp.__gmpq_cmp
_MPQ_set_str = _libgmp.__gmpq_set_str
_MPQ_get_str = _libgmp.__gmpq_get_str

# Gnu MP random generator algorithms
RAND_ALGO_DEFAULT = _GMP_randinit_default
RAND_ALGO_MT = _GMP_randinit_mt


#------------------------------------------------------------------------------
# Wrappers around Gnu MP Integer, Rational, Random, Float
#------------------------------------------------------------------------------


class Integer(object):
  """GNU MP arbitrarily long integer."""

  def __init__(self, init_value=0):
    self._mpz = c_mpz_struct()
    self._mpzp = ctypes.byref(self._mpz)
    _MPZ_init(self)
    self.set(init_value)

  def __del__(self):
    _MPZ_clear(self)

  @property
  def _as_parameter_(self):
    """as parameter."""
    return self._mpzp

  @staticmethod
  def from_param(arg):
    """From param."""
    assert isinstance(arg, Integer)
    return arg

  def _apply_ret(self, func, ret, op1, op2):
    """Applies a GNU MP function over arguments and returns a result."""
    #assert isinstance(ret, Integer)
    if not isinstance(op1, Integer):
      op1 = Integer(op1)
    if not isinstance(op2, Integer):
      op2 = Integer(op2)
    func(ret, op1, op2)
    return ret

  def _apply_2_rets(self, func, ret1, ret2, op1, op2):
    """Applies a GNU MP function over arguments and returns a tuple."""
    #assert isinstance(ret1, Integer)
    #assert isinstance(ret2, Integer)
    if not isinstance(op1, Integer):
      op1 = Integer(op1)
    if not isinstance(op2, Integer):
      op2 = Integer(op2)
    func(ret1, ret2, op1, op2)
    return ret1, ret2

  def _apply_ret_2_0(self, func, ret, op1):
    """Applies a GNU MP function over arguments and returns a result."""
    #assert isinstance(ret, Integer)
    #assert isinstance(op1, Integer)
    func(ret, op1)
    return ret

  def _apply_ret_2_1(self, func, op1, op2):
    """Applies a GNU MP function over arguments and returns a result."""
    if not isinstance(op1, Integer):
      op1 = Integer(op1)
    if not isinstance(op2, Integer):
      op2 = Integer(op2)
    return func(op1, op2)

  def set(self, value):
    """Set integer."""
    if isinstance(value, Integer):
      _MPZ_set_str(self, value._tobytes(), 10)
    else:
      try:
        _MPZ_set_str(self, number_to_pybytes(int(value)), 10)
      except Exception:
        raise TypeError("non an integer")

  def _tobytes(self):
    """To Python byte string."""
    return _MPZ_get_str(None, 10, self)

  def __str__(self):
    return to_str(self._tobytes())

  def __repr__(self):
    return self.__str__()

  def __lt__(self, other):
    return self._apply_ret_2_1(_MPZ_cmp, self, other) < 0

  def __le__(self, other):
    return self.__lt__(other) or self.__eq__(other)

  def __eq__(self, other):
    return self._apply_ret_2_1(_MPZ_cmp, self, other) == 0

  def __ne__(self, other):
    return not self.__eq__(other)

  def __gt__(self, other):
    return self._apply_ret_2_1(_MPZ_cmp, self, other) > 0

  def __ge__(self, other):
    return self.__gt__(other) or self.__eq__(other)

  def __add__(self, other):
    return self._apply_ret(_MPZ_add, Integer(), self, other)

  def __sub__(self, other):
    return self._apply_ret(_MPZ_sub, Integer(), self, other)

  def __mul__(self, other):
    return self._apply_ret(_MPZ_mul, Integer(), self, other)

  def __divmod__(self, divisor):
    if divisor == 0 or divisor == Integer():
      raise ZeroDivisionError("integer division or modulo by zero")
    return self._apply_2_rets(_MPZ_fdivmod,
                              Integer(), Integer(), self, divisor)

  def __rdivmod__(self, dividend):
    if self == 0 or self == Integer():
      raise ZeroDivisionError("integer division or modulo by zero")
    return self._apply_2_rets(_MPZ_fdivmod,
                              Integer(), Integer(), dividend, self)

  def __div__(self, other):
    return self.__floordiv__(other)

  def __truediv__(self, unused_other):
    raise NotImplementedError("True division is not supported.")

  def __floordiv__(self, other):
    if other == 0 or other == Integer():
      raise ZeroDivisionError("integer division or modulo by zero")
    return self._apply_ret(_MPZ_fdiv, Integer(), self, other)

  def __and__(self, other):
    return self._apply_ret(_MPZ_and, Integer(), self, other)

  def __mod__(self, other):
    if other == 0 or other == Integer():
      raise ZeroDivisionError("integer division or modulo by zero")
    return self._apply_ret(_MPZ_fmod, Integer(), self, other)

  def __xor__(self, other):
    return self._apply_ret(_MPZ_xor, Integer(), self, other)

  def __or__(self, other):
    return self._apply_ret(_MPZ_ior, Integer(), self, other)

  def __iadd__(self, other):
    return self._apply_ret(_MPZ_add, self, self, other)

  def __isub__(self, other):
    return self._apply_ret(_MPZ_sub, self, self, other)

  def __imul__(self, other):
    return self._apply_ret(_MPZ_mul, self, self, other)

  def __imod__(self, other):
    return self._apply_ret(_MPZ_fmod, self, self, other)

  def __idiv__(self, other):
    return self.__floordiv__(other)

  def __itruediv__(self, unused_other):
    raise NotImplementedError("True division is not supported.")

  def __ifloordiv__(self, other):
    if other == 0 or other == Integer():
      raise ZeroDivisionError("integer division or modulo by zero")
    return self._apply_ret(_MPZ_fdiv, self, self, other)

  def __iand__(self, other):
    return self._apply_ret(_MPZ_and, self, self, other)

  def __ixor__(self, other):
    return self._apply_ret(_MPZ_xor, self, self, other)

  def __ior__(self, other):
    return self._apply_ret(_MPZ_ior, self, self, other)

  def __radd__(self, other):
    return self._apply_ret(_MPZ_add, Integer(), other, self)

  def __rsub__(self, other):
    return self._apply_ret(_MPZ_sub, Integer(), other, self)

  def __rmul__(self, other):
    return self._apply_ret(_MPZ_mul, Integer(), other, self)

  def __rdiv__(self, other):
    return self.__rfloordiv__(other)

  def __rtruediv__(self, unused_other):
    raise NotImplementedError("True division is not supported.")

  def __rfloordiv__(self, other):
    if self == 0 or self == Integer():
      raise ZeroDivisionError("integer division or modulo by zero")
    return self._apply_ret(_MPZ_fdiv, Integer(), other, self)

  def __rmod__(self, other):
    if self == 0 or self == Integer():
      raise ZeroDivisionError("integer division or modulo by zero")
    return self._apply_ret(_MPZ_fmod, Integer(), other, self)

  def __abs__(self):
    return self._apply_ret_2_0(_MPZ_abs, Integer(), self)

  def __neg__(self):
    return self._apply_ret_2_0(_MPZ_neg, Integer(), self)


# class Rational(object):
#   def __init__(self):
#     self._mpq = c_mpq_struct()
#     self._mpqp = ctypes.byref(self._mpq)
#     _MPQ_init(self)
#
#   def __del__(self):
#     _MPQ_clear(self)
#
#   @property
#   def _as_parameter_(self):
#     return self._mpqp
#
#   @staticmethod
#   def from_param(arg):
#     assert isinstance(arg, Rational)
#     return arg
#
#   def __apply_ret(self, func, ret, op1, op2):
#     assert isinstance(ret, Rational)
#     if not isinstance(op1, Rational):
#       op1 = Rational(op1)
#     if not isinstance(op2, Rational):
#       op2 = Rational(op2)
#     func(ret, op1, op2)
#     return ret
#
#   def __apply_ret_2_0(self, func, ret, op1):
#     assert isinstance(ret, Rational)
#     assert isinstance(op1, Rational)
#     func(ret, op1)
#     return ret
#
#   def __apply_ret_2_1(self, func, op1, op2):
#     if not isinstance(op1, Rational):
#       op1 = Rational(op1)
#     if not isinstance(op2, Rational):
#       op2 = Rational(op2)
#     return func(op1, op2)
#
#   def set(self, value):
#     if isinstance(value, Rational):
#       _MPQ_set_str(self, value.__str__(), 10)
#     else:
#       try:
#         _MPQ_set_str(self, str(float(value)), 10)
#       except Exception:
#         raise TypeError("non-rational")
#
#   def __str__(self):
#     return _MPQ_get_str(None, 10, self)
#
#   def __repr__(self):
#     return self.__str__()
#
#   def __lt__(self, other):
#     return self.__apply_ret_2_1(_MPQ_cmp, self, other) < 0
#
#   def __le__(self, other):
#     return self.__lt__(other) or self.__eq__(other)
#
#   def __eq__(self, other):
#     return self.__apply_ret_2_1(_MPQ_cmp, self, other) == 0
#
#   def __ne__(self, other):
#     return not self.__eq__(other)
#
#   def __gt__(self, other):
#     return self.__apply_ret_2_1(_MPQ_cmp, self, other) > 0
#
#
#   def __ge__(self, other):
#     return self.__gt__(other) or self.__eq__(other)
#
#   def __add__(self, other):
#     return self.__apply_ret(_MPQ_add, Rational(), self, other)
#
#   def __sub__(self, other):
#     return self.__apply_ret(_MPQ_sub, Rational(), self, other)
#
#   def __mul__(self, other):
#     return self.__apply_ret(_MPQ_mul, Rational(), self, other)
#
#   def __iadd__(self, other):
#     return self.__apply_ret(_MPQ_add, self, self, other)
#
#   def __isub__(self, other):
#     return self.__apply_ret(_MPQ_sub, self, self, other)
#
#   def __imul__(self, other):
#     return self.__apply_ret(_MPQ_mul, self, self, other)
#
#   def __abs__(self):
#     return self.__apply_ret_2_0(_MPQ_abs, Rational(), self)
#
#   def __neg__(self):
#     return self.__apply_ret_2_0(_MPQ_neg, Rational(), self)
#
#
# class Float(object):
#   def __init__(self, init_value=0.0, precision=None):
#     self._mpf = c_mpf_struct()
#     self._mpfp = ctypes.byref(self._mpf)
#     _MPF_init(self)
#     self.set(init_value)
#
#   def __del__(self):
#     _MPF_clear(self)
#
#   def set(self, value):
#     if isinstance(value, Float):
#       _MPF_set_str(self, value.__str__(), 10)
#     else:
#       try:
#         _MPF_set_str(self, str(float(value)), 10)
#       except Exception:
#         raise TypeError("non-float")
#
#   def __apply_ret(self, func, ret, op1, op2):
#     assert isinstance(ret, Float)
#     if not isinstance(op1, Float):
#       op1 = Float(op1)
#     if not isinstance(op2, Float):
#       op2 = Float(op2)
#     func(ret, op1, op2)
#     return ret
#
#   def __apply_ret_2_0(self, func, ret, op1):
#     assert isinstance(ret, Float)
#     assert isinstance(op1, Float)
#     func(ret, op1)
#     return ret
#
#   def __apply_ret_2_1(self, func, op1, op2):
#     if not isinstance(op1, Float):
#       op1 = Float(op2)
#     if not isinstance(op2, Float):
#       op2 = Float(op2)
#     return func(op1, op2)
#
#   #Extra apply_ret for 3 args with return - for _eq
#   def __apply_ret_3_1(self, func, op1, op2, op3):
#     if not isinstance(op2, Float):
#       op2 = Float(op2)
#     return func(op1, op2, op3)
#
#   @property
#   def _as_parameter_(self):
#     return self._mpfp
#
#   @staticmethod
#   def from_param(arg):
#     assert isinstance(arg, Float)
#     return arg
#
#   def __str__(self):
#     exp = (ctypes.c_byte * 4)()
#     exp = ctypes.cast(exp, ctypes.POINTER(ctypes.c_int))
#     return _MPF_get_str(None, exp, 10, 10, self)
#
#   def __repr__(self):
#     return self.__str__()
#
#   def __lt__(self, other):
#     return self.__apply_ret_2_1(_MPF_cmp, self, other) < 0
#
#   def __le__(self, other):
#     return self.__lt__(other) or self.__eq__(other)
#
#   def __eq__(self, other):
#     return self.__apply_ret_3_1(_MPF_eq, self, other, ctypes.c_int(32)) != 0
#
#   def __ne__(self, other):
#     return not self.__eq__(other)
#
#   def __gt__(self, other):
#     return self.__apply_ret_2_1(_MPF_cmp, self, other) > 0
#
#   def __ge__(self, other):
#     return self.__gt__(other) or self.__eq__(other)
#
#   def __add__(self, other):
#     return self.__apply_ret(_MPF_add, Float(), self, other)
#
#   def __sub__(self, other):
#     return self.__apply_ret(_MPF_sub, Float(), self, other)
#
#   def __mul__(self, other):
#     return self.__apply_ret(_MPF_mul, Float(), self, other)
#
#   def __div__(self, other):
#     return self.__apply_ret(_MPF_div, Float(), self, other)
#
#   def __iadd__(self, other):
#     return self.__apply_ret(_MPF_add, self, self, other)
#
#   def __isub__(self, other):
#     return self.__apply_ret(_MPF_sub, self, self, other)
#
#   def __imul__(self, other):
#     return self.__apply_ret(_MPF_mul, self, self, other)
#
#   def __radd__(self, other):
#     return self.__apply_ret(_MPF_add, Float(), other, self)
#
#   def __rsub__(self, other):
#     return self.__apply_ret(_MPF_sub, Float(), other, self)
#
#   def __rmul__(self, other):
#     return self.__apply_ret(_MPF_mul, Float(), other, self)
#
#   def __rdiv__(self, other):
#     return self.__apply_ret(_MPF_div, Float(), other, self)
#
#   def __idiv__(self, other):
#     return self.__apply_ret(_MPF_div, self, self, other)
#
#   def __abs__(self):
#     return self.__apply_ret_2_0(_MPF_abs, Float(), self)
#
#   def __neg__(self):
#     return self.__apply_ret_2_0(_MPF_neg, Float(), self)
#
#
# class Random(object):
#   def __init__(self, algo=RAND_ALGO_DEFAULT):
#     self._gmp = c_gmp_randstate_struct()
#     self._gmpp = ctypes.byref(self._gmp)
#
#     if algo in [RAND_ALGO_DEFAULT, RAND_ALGO_MT]:
#       algo(self)
#     else:
#       raise NotImplementedError("Algorithm not available")
#
#   def __del__(self):
#     _GMP_randclear(self)
#
#   @property
#   def _as_parameter_(self):
#     return self._gmpp
#
#   @staticmethod
#   def from_param(arg):
#     assert isinstance(arg, Random)
#     return arg
#
#   def __apply_ret(self, func, ret, op1, op2):
#     func(ret, op1, op2)
#     return ret
#
#   def seed(self, s):
#     if not isinstance(s, Integer):
#       s = Integer(s)
#       _GMP_randseed(self, s)
#
#   def urandom(self, n):
#     ret = Integer()
#     if not isinstance(n, Integer):
#       n = Integer(n)
#       _GMP_urandomm(ret, self, n)
#     return ret


#------------------------------------------------------------------------------
# Argument/return-type specs for Gnu MP routines
#------------------------------------------------------------------------------

## Gnu MP random generator routines
#_GMP_randinit_default.argtypes = (Random,)
#_GMP_randinit_mt.artypes = (Random,)
#_GMP_randclear.argtypes = (Random,)
#_GMP_randseed.argtypes = (Random, Integer)
#_GMP_urandomm.argtypes = (Integer, Random, Integer)

# Gnu MP integer routines
_MPZ_init.argtypes = (Integer,)
_MPZ_clear.argtypes = (Integer,)
_MPZ_add.argtypes = (Integer, Integer, Integer)
_MPZ_sub.argtypes = (Integer, Integer, Integer)
_MPZ_mul.argtypes = (Integer, Integer, Integer)
_MPZ_mod.argtypes = (Integer, Integer, Integer)
_MPZ_and.argtypes = (Integer, Integer, Integer)
_MPZ_ior.argtypes = (Integer, Integer, Integer)
_MPZ_xor.argtypes = (Integer, Integer, Integer)
_MPZ_abs.argtypes = (Integer, Integer)
_MPZ_neg.argtypes = (Integer, Integer)
_MPZ_cmp.argtypes = (Integer, Integer)
_MPZ_set_str.argtypes = (Integer, ctypes.c_char_p, ctypes.c_int)
_MPZ_get_str.argtypes = (ctypes.c_char_p, ctypes.c_int, Integer,)
# non-default (int) return types
_MPZ_get_str.restype = ctypes.c_char_p

# Gnu MP rational number routines
#_MPQ_init.argtypes = (Rational,)
#_MPQ_clear.argtypes = (Rational,)
#_MPQ_add.argtypes = (Rational, Rational, Rational)
#_MPQ_sub.argtypes = (Rational, Rational, Rational)
#_MPQ_mul.argtypes = (Rational, Rational, Rational)
#_MPQ_abs.argtypes = (Rational, Rational)
#_MPQ_neg.argtypes = (Rational, Rational)
#_MPQ_cmp.argtypes = (Rational, Rational)
#_MPQ_set_str.argtypes = (Rational, ctypes.c_char_p, ctypes.c_int)
#_MPQ_get_str.argtypes = (ctypes.c_char_p, ctypes.c_int, Rational,)
## non-default (int) return types
#_MPQ_get_str.restype = ctypes.c_char_p

# Gnu MP floating point routines
#_MPF_set_default_prec.argtypes = (ctypes.c_ulong,)
#_MPF_init.argtypes = (Float,)
#_MPF_clear.argtypes = (Float,)
#_MPF_add.argtypes = (Float, Float, Float)
#_MPF_sub.argtypes = (Float, Float, Float)
#_MPF_mul.argtypes = (Float, Float, Float)
#_MPF_abs.argtypes = (Float, Float)
#_MPF_neg.argtypes = (Float, Float)
#_MPF_cmp.argtypes = (Float, Float)
#_MPF_eq.argtypes = (Float, Float, ctypes.c_int)
#_MPF_set_str.argtypes = (Float, ctypes.c_char_p, ctypes.c_int)
#_MPF_get_str.argtypes = (ctypes.c_char_p, ctypes.POINTER(ctypes.c_int),
#                         ctypes.c_int, ctypes.c_int, Float)
## non-default (int) return types
#_MPF_get_str.restype = ctypes.c_char_p
