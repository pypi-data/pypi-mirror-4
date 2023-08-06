#############################################################################
# The finance package is open source under the `Python Software Foundation  #
# License <http://www.opensource.org/licenses/PythonSoftFoundation.php>`_   #
#############################################################################

'''
**The decimalpy.decimalmetafunctions**

This module contains mathematical functions on functions such as numerical
first and second order derivative.
Also it contains tools in order to do decimal calculations.
'''

from decimal import Decimal, getcontext


def decimal_simple_poly_exponent(base,
                                 exponent,
                                 factor=Decimal('1'),
                                 addend=Decimal('0')
                                 ):
    '''Returns :math:`factor \cdot {base}^{exponent} + addend`, all
    arguments are transformed to Decimals.
    It is used for standardizing basic calculations.

    **Usage**
    Calculate :math:`2^3`:
    >>> decimal_simple_poly_exponent(2, 3)
    Decimal('8')

    Calculate :math:`2^3 + 3`:
    >>> decimal_simple_poly_exponent(2, 3, 1, 3)
    Decimal('11')

    Calculate :math:`4 \cdot 2^3 + 3`:
    >>> decimal_simple_poly_exponent(2, 3, 4, 3)
    Decimal('35')
    '''
    factor = to_decimal(factor)
    base = to_decimal(base)
    exponent = to_decimal(exponent)
    addend = to_decimal(addend)
    if exponent == Decimal('0'):
        return factor + addend
    elif base == Decimal('0'):
        return addend
    else:
        if base < Decimal('0'):
            if exponent._isinteger():
                return base ** exponent * factor + addend
            else:
                return Decimal('NaN')
        else:
            return base ** exponent * factor + addend


def to_decimal(value):
    '''Converts a string (if possible) or a number to a Decimal.
    Returns None if input value cannot be converted.
    This way it can be used for validation as well.

    **Usage**

    >>> to_decimal(1)
    Decimal('1')
    >>> to_decimal(1.2)
    Decimal('1.2')
    >>> to_decimal('text')

    >>> to_decimal('1.2')
    Decimal('1.2')
    '''
    try:
        return Decimal(str(value))
    except:
        return None


def to_integer(value):
    '''Return input value as an integer.
    Returns None if input value cannot be converted.
    Arguments like Float or Decimal have their integer part returned.
    This way it can be used for validation as well.

    **Usage**

    >>> to_integer(5)
    5
    >>> to_integer(5.0)
    5
    >>> to_integer(5.01)
    5
    >>> to_integer(Decimal('-3.56'))
    -3
    '''
    try:
        return int(value)
    except:
        return None


def round_decimal(value, nbr_of_decimals=7, rounding_method='ROUND_HALF_UP'):
    '''Rounds off a Decimal by nbr_of_decimals using rounding_method.
    Decimal should be used whenever one is doing financial calculations.
    Decimal avoids small errors due number representation etc.
    In other words calculations become similar to those in spreadsheets like
    eg Excel.

    Possible rounding methods are:
        * ROUND_CEILING - Always round upwards towards infinity
        * ROUND_DOWN - Always round toward zero
        * ROUND_FLOOR - Always round down towards negative infinity
        * ROUND_HALF_DOWN - Rounds away from zero if the last significant
          digit is greater than or equal to 5, otherwise toward zero
        * ROUND_HALF_EVEN - Like ROUND_HALF_DOWN except that if the value is 5
          then the preceding digit is examined. Even values cause the result
          to be rounded down and odd digits cause the result to be rounded up
        * ROUND_HALF_UP - Like ROUND_HALF_DOWN except if the last significant
          digit
          is 5 the value is rounded away from zero
        * ROUND_UP - Round away from zero
        * ROUND_05UP - Round away from zero if the last digit is 0 or 5,
          otherwise towards zero
    '''
    if isinstance(nbr_of_decimals, int):
        value = to_decimal(value)
        if value:
            getcontext().rounding = rounding_method
            return value.quantize(Decimal('.1') ** nbr_of_decimals)
    return


def decimal_division(numerator, denominator):
    '''Standardize division. If denominator is zero, Decimal('NaN') is
    returned

    **Usage**

    >>> decimal_division(Decimal('5'), Decimal('3'))
    Decimal('1.666666666666666666666666667')
    >>> decimal_division(Decimal('5'), Decimal('0'))
    Decimal('NaN')
    '''
    if isinstance(numerator, Decimal) and isinstance(denominator, Decimal):
        if denominator != Decimal('0'):
            return numerator / denominator
    return Decimal('NaN')


class NumericalFirstOrder:
    '''Is instantiated with a countinous derivable function and a possible
    step size (default = Decimal('0.0001')) for the numerical differentiation.

    **How to use:**

    >>> import decimalpy as dp
    >>> deriv_log = dp.NumericalFirstOrder(dp.decimal_log)
    >>> for x in (1, float(2), Decimal('8')): # must be (1, 0.5, 0.125)
    ...     print deriv_log(x)
    ...
    0.9999999999999999199999971433
    0.49999999999999999749999975
    0.1249999999999999999975558333
    >>> isinstance(deriv_log(4), Decimal)
    True


    References:

    #. http://amath.colorado.edu/faculty/fornberg/Docs/MathComp_88_FD_formulas.pdf
    #. http://en.wikipedia.org/wiki/Numerical_differentiation
    #. http://en.wikipedia.org/wiki/Lagrange_polynomial
    #. http://www.math-linux.com/spip.php?article71
    #. http://www.proofwiki.org/wiki/Lagrange_Polynomial_Approximation
    #. http://people.maths.ox.ac.uk/trefethen/barycentric.pdf
    '''
    def __init__(self, function, step_size=Decimal('0.0001')):
        ''':param function: A function
        :type function: A one dimensional function accepting and returning
        Decimal as values
        :param step_size: A number specifying the step size
        :type step_size: Decimal or float
        '''
        self.function = function
        self.step_size = Decimal('%s' % step_size)

    def __call__(self, x_value):
        ''':param x_value: A value
        :type x_value: a positive integer, float or decimal
        :return: The first order derivative at the x_value
        '''
        x_value = to_decimal(x_value)
        if x_value:
            upper2 = self.function(x_value + 2 * self.step_size)
            lower2 = self.function(x_value - 2 * self.step_size)
            upper1 = self.function(x_value + self.step_size)
            lower1 = self.function(x_value - self.step_size)
            return ((8 * (upper1 - lower1) - (upper2 - lower2))
                    / self.step_size / Decimal('12'))


class NumericalSecondOrder:
    '''Is instantiated with a countinous derivable function and a possible step
    size (default = Decimal('0.0001')) for the numerical differentiation.

    **How to use:**

    >>> import decimalpy as dp
    >>> curvature = dp.NumericalSecondOrder(dp.decimal_log)
    >>> for x in (1, float(2), Decimal('4')): # must be (-1, -0.25, -0.0625)
    ...     print curvature(x)
    ...
    -0.9999999999999998666666641667
    -0.2499999999999999978333333333
    -0.06250000000000000009166666667

    References:

    #. http://amath.colorado.edu/faculty/fornberg/Docs/MathComp_88_FD_formulas.pdf
    #. http://en.wikipedia.org/wiki/Numerical_differentiation
    #. http://en.wikipedia.org/wiki/Lagrange_polynomial
    #. http://www.math-linux.com/spip.php?article71
    #. http://www.proofwiki.org/wiki/Lagrange_Polynomial_Approximation
    #. http://people.maths.ox.ac.uk/trefethen/barycentric.pdf
    '''

    def __init__(self, function, step_size=Decimal('0.0001')):
        ''':param function: A function
        :type function: A one dimensional function accepting and returning
        Decimal as values
        :param step_size: A number specifying the step size
        :type step_size: Decimal or float
        '''
        self.function = function
        self.step_size = Decimal('%s' % step_size)

    def __call__(self, x_value):
        ''':param x_value: A value
        :type x_value: a positive integer, float or decimal
        :return: The first order derivative at the x_value
        '''
        x_value = to_decimal(x_value)
        if x_value:
            upper2 = self.function(x_value + 2 * self.step_size)
            lower2 = self.function(x_value - 2 * self.step_size)
            upper1 = self.function(x_value + self.step_size)
            lower1 = self.function(x_value - self.step_size)
            middle = self.function(x_value)
            return ((-30 * middle + 16 * (upper1 + lower1) - (upper2 + lower2))
                    / self.step_size / self.step_size / Decimal('12'))


class DecimalSolver:
    '''DecimalSolver
    **How to use:**

    >>> from decimal import Decimal
    >>> import decimalpy as dp
    >>> f = lambda x: x*x
    >>> numeric_sqrt = DecimalSolver(f)
    >>> for x in [4, 9.0, Decimal('16')]:
    ...     print numeric_sqrt(x, 1)
    2.000000000000002158638110942
    3.000000000000000000325260652
    4.000000000000050672229330380
    '''
    def __init__(self,
                function,
                derivative=None,
                precision=Decimal('1e-6'),
                max_iteration=30
                ):
        self.function = function
        if derivative:
            self.derivative = derivative
        else:
            self.derivative = NumericalFirstOrder(function)
        self.precision = Decimal('%s' % precision)
        if isinstance(max_iteration, int):
            self.max_iteration = max_iteration
        else:
            self.max_iteration = 30

    def __call__(self,
                 target,
                 minimum=Decimal('0'),  # Or start value
                 maximum=None
                 ):
        '''
        The structure is copied from [Kiusalaas]_ p. 155, newtonRaphson
        '''
        target = to_decimal(target)
        minimum = to_decimal(minimum)
        if target and isinstance(minimum, Decimal):
            maximum = to_decimal(maximum)
            bracketed = False
            if maximum:
                diff_min = target - self.function(minimum)
                diff_max = target - self.function(maximum)
                bracketed = (diff_min * diff_max > 0)
            value = minimum
            for i in range(self.max_iteration):
                use_bisection = False
                diff = target - self.function(value)
                try:
                    delta = diff / self.derivative(value)
                    value += delta
                    use_bisection = bracketed and not minimum <= value <= maximum
                except ZeroDivisionError:
                    if bracketed:
                        use_bisection = True
                        if minimum <= value <= maximum and diff * diff_min:
                            maximum = value
                        if minimum <= value <= maximum and diff * diff_max:
                            minimum = value
                    else:
                        raise ZeroDivisionError(
                        'Division by derivative value equal to zero')
                if use_bisection:
                    value = (maximum + maximum) * Decimal('0.5')
                    delta = (maximum - maximum) * Decimal('0.5')
                if abs(delta) < self.precision:
                    return value
            raise Exception('Precision cannot be meet by iterations')


if __name__ == '__main__':
    import doctest
    doctest.testmod()