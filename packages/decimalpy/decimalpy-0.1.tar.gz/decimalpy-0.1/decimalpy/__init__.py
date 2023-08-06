#############################################################################
# The finance package is open source under the `Python Software Foundation  #
# License <http://www.opensource.org/licenses/PythonSoftFoundation.php>`_   #
#############################################################################

'''
*********************************
The decimalpy package for Python!
*********************************

Introduction
============

It has been decided to use the datatype Decimal as base for al calculations
in the `finance <..//rstFiles/200%20PythonHacks.html#the-finance-package>`_
package.

There are 2 reasons for this:

#. In finance decimals matters and when other financial systems use the IEEE
   standard 854-1987 the package finance need to do the same
#. For valuation purposes it is important that the financial calculations are
   the exact same as those performed in eg spreadsheets

`See also the chapter that examplifies the reasons for this. <..//rstFiles/600%20On%20Python.html#arrays-for-financial-calculations>`_

The Package decimalpy is inspired by `numpy <http://numpy.scipy.org>`_ and
eg the vector concept of `The R package <http://www.r-project.org>`_.
The key difference from numpy is that in decimalpy the only number type is
decimal.

The Package contains:

* An n-dimensional array of decimals, a decimalvector
* An n-dimensional array of decimals where the keys can be of a specific
  type and not just integers as in a decimalvector, a
  SortedKeysDecimalValuedDict
* A decorator decimalvector_function that converts a simpel function into a
  function that given a decimalvector as an argument returns a decimalvector
  of function values. This makes it fairly easy to extend the number of
  decimalvector functions. Also decimalvector functions makes it fairly easy
  to use other packages like eg matplotlib
* A set of decimalvector (typically financial) functions
* Meta functions (functions on functions) for numerical first
  (NumericalFirstOrder) and second (NumericalSecondOrder) order differention
* A meta function for finding the inverse value of a function

The package will be extended in order to support the needs in the package
`finance <..//rstFiles/200%20PythonHacks.html#the-finance-package>`_ .

The finance package is open source under the `Python Software Foundation
License <http://www.opensource.org/licenses/PythonSoftFoundation.php>`_

Class definitions and documentation
===================================

'''
__version__ = '0.1a beta'

from decimaltypes import DecimalVector, decimalvector_function, \
     PolyExponents, SortedKeysDecimalValuedDict
from decimalfunctions import decimal_exp, decimal_log, PiecewiseConstant, \
     LinearSpline, NaturalCubicSpline, FinancialCubicSpline
from decimalmetafunctions import NumericalFirstOrder, NumericalSecondOrder, \
     DecimalSolver, to_decimal, round_decimal

__all__ = [
    DecimalVector,
    SortedKeysDecimalValuedDict,
    PolyExponents,
    decimalvector_function,
    decimal_exp,
    decimal_log,
    PiecewiseConstant,
    LinearSpline,
    NaturalCubicSpline,
    FinancialCubicSpline,
    round_decimal,
    to_decimal,
    NumericalFirstOrder,
    NumericalSecondOrder,
    DecimalSolver
]