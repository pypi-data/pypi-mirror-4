#############################################################################
# The finance package is open source under the `Python Software Foundation  #
# License <http://www.opensource.org/licenses/PythonSoftFoundation.php>`_   #
#############################################################################

'''
**The decimalpy.decimalfunctions**

This module contains mathematical functions that given a list or a
decimalvector returns a DecimalVector.
In case of an input like a integer, float or a Decimal the result is returned
as a Decimal.
'''

import locale
from decimal import Decimal
from decimaltypes import decimalvector_function as _decimalvector_function, \
                         DecimalVector


class LUdecomp3:
    '''Function class to solve triagonal matrix equations. It is used for the
    splines calculations.

    **At instatiation:**

    :param lower_diagonal: Lower diagonal in the tridiagonal matrix
    :type lower_diagonal: (n-1)-dimensional DecimalVector
    :param diagonal: The diagonal in the tridiagonal matrix
    :type diagonal: non-zero n-dimensional DecimalVector
    :param upper_diagonal: Upper diagonal in the tridiagonal matrix
    :type upper_diagonal: A (n-1)-dimensional DecimalVector
    :return: The LU decomposed matrix of and triagonal matrix
             [lower_diagonal, diagonal, upper_diagonal]

    **When called as function:**

    :param b: b in the equation:
        [lower_diagonal, diagonal, upper_diagonal]x = b
    :type b: A n-dimensional DecimalVector
    :return: The solution, x, to the equation:
                [lower_diagonal, diagonal, upper_diagonal]x = b

    **How to use:**

    [Kiusalaas]_ p. 66, example 2.11

    >>> lower_diagonal = DecimalVector(4, -1.)
    >>> diagonal = DecimalVector(5, 2.)
    >>> upper_diagonal = DecimalVector(4, -1.)
    >>> # Instantiation
    >>> f = LUdecomp3(lower_diagonal, diagonal, upper_diagonal)
    >>> # f is just called as a function
    >>> print f([5., -5., 4., -5., 5.])
    DecimalVector([2, -1, 1, -1, 2.0000000000000000000000000])

    **Reference:**

    #. [Kiusalaas]_ p. 59

    '''
    def __init__(self, lower_diagonal, diagonal, upper_diagonal):
        assert isinstance(lower_diagonal, DecimalVector), \
            'Lower diagonal must be a DecimalVector'
        assert isinstance(diagonal, DecimalVector), \
            'Diagonal must be a DecimalVector'
        assert isinstance(upper_diagonal, DecimalVector), \
            'Upper diagonal must be a DecimalVector'
        assert len(diagonal) - 1 == \
            len(upper_diagonal) == len(lower_diagonal), \
            'DecimalVectors are not of proper lengths'
        dimension = len(diagonal)
        for k in range(1, dimension):
            # d must be non-zero
            lam = lower_diagonal[k - 1] / diagonal[k - 1]
            diagonal[k] = diagonal[k] - lam * upper_diagonal[k - 1]
            lower_diagonal[k - 1] = lam
        self.lower_diagonal = lower_diagonal
        self.diagonal = diagonal
        self.upper_diagonal = upper_diagonal

    def __call__(self, in_out):
        in_out = DecimalVector(in_out)
        dimension = len(self.diagonal)
        for k in range(1, dimension):
            in_out[k] = in_out[k] - self.lower_diagonal[k - 1] * in_out[k - 1]
        in_out[dimension - 1] = in_out[dimension - 1] \
                                / self.diagonal[dimension - 1]
        for k in range(dimension - 2, -1, -1):
            in_out[k] = (in_out[k] - self.upper_diagonal[k] * in_out[k + 1]) \
                        / self.diagonal[k]
        return in_out


class NaturalCubicSpline:
    '''Function class for doing natural cubic spline interpolation.
    A linear extrapolation is used outside the interval of the x-values.

    **At instantiation:**

    :param x_data: Array of x-coordinates
    :type x_data: A n-dimensional numpy array of float or decimal
    :param y_data: Array of y-coordinates
    :type y_data: A n-dimensional numpy array of float or decimal

    At instantion the class function is prepared to calculate y-values for
    x-values according to the natural cubic spline.

    Extrapolation is linear from the endpoints with the slope like the one at
    the endpoint.

    **When called as a function:**

    :param x: The value to interpolate from
    :type x: A real number
    :param degree: What kind of value to return for x
    :type degree: 0 (y-value), 1 (slope), 2 (curvature)
    :return: The corresponding y-value for x value according
      to the natural cubic spline and the points from instatiation

    **How to use:**

    [Kiusalaas]_ p. 119

    >>> x_data = DecimalVector([1, 2, 3, 4, 5])
    >>> y_data = DecimalVector([0, 1, 0, 1, 0])
    >>> # Instantiation
    >>> f = NaturalCubicSpline(x_data, y_data)
    >>> # f is just called as a function

    >>> print f(1.5), f(4.5)
    0.7678571428571428571428571427 0.7678571428571428571428571427
    >>> print f(1.5, 1), f(4.5, 1)
    1.178571428571428571428571429 -1.178571428571428571428571428
    >>> print f(1.5, 2), f(4.5, 2)
    -2.142857142857142857142857142 -2.142857142857142857142857143

    Call the function with a tuple, list or an array

    >>> print f([1.5, 4.5])
    DecimalVector([0.7678571428571428571428571427, 0.7678571428571428571428571427])
    >>> print f([1.5, 4.5], 1)
    DecimalVector([1.178571428571428571428571429, -1.178571428571428571428571428])
    >>> print f([1.5, 4.5], 2)
    DecimalVector([-2.142857142857142857142857142, -2.142857142857142857142857143])

    **Reference:**

    #. [Kiusalaas]_ p. 118, p. 191

    '''
    def __init__(self, x_data, y_data):
        x_data = DecimalVector(x_data)
        y_data = DecimalVector(y_data)
        assert len(x_data) == len(y_data), \
            'DecimalVectors are not of proper lengths'
        dimension = len(x_data)
        lower_diagonal = DecimalVector(dimension - 1, 0)
        diagonal = DecimalVector(dimension, 1)
        upper_diagonal = DecimalVector(dimension - 1, 0)
        target = DecimalVector(dimension, 0)
        d_x = x_data[1:] - x_data[0:-1]  # length = dimension-1
        d_y = y_data[1:] - y_data[0:-1]  # length = dimension-1
        # lower_diagonal[dimension-1] = 0
        lower_diagonal[0:dimension - 2] = d_x[0:-1]
        # diagonal[0] = diagonal[dimension] = 1
        diagonal[1:dimension - 1] = 2.0 * (d_x[1:] + d_x[0:-1])
        # upper diagonal[0] = 0
        upper_diagonal[1:dimension - 1] = d_x[1:dimension - 1]
        # target[0] = target[dimension] = 0
        target[1:dimension - 1] = 6.0 * (d_y[1:] / d_x[1:] \
                                - d_y[0:-1] / d_x[0:-1])
        self.x_data = x_data
        self.y_data = y_data
        lu_decomp = LUdecomp3(lower_diagonal, diagonal, upper_diagonal)
        self.target = lu_decomp(target)

    def __str__(self):
        # __str__ is not defined at base function
        points = zip(self.x_data, self.y_data)
        return 'Natural cubic spline based on points:\n.. %s' % \
               '\n.. '.join(['(%.4f, %.4f)' % p for p in points])

    __repr__ = __str__

    @_decimalvector_function(1, argument_is_decimal=True)
    def __call__(self, x_value, degree=0):
        if self.x_data[0] <= x_value <= self.x_data[-1]:
            return self._interpolate(x_value, degree)
        elif x_value > self.x_data[-1]:
            x_0, y_0 = self.x_data[-1], self.y_data[-1]
            slope = self._interpolate(x_0, 1)
        else:
            x_0, y_0 = self.x_data[0], self.y_data[0]
            slope = self._interpolate(x_0, 1)
        if degree == 1:
            return slope
        elif degree == 2:
            return 0
        else:
            return slope * (x_value - x_0) + y_0

    def _interpolate(self, x_value, degree=0):
        '''Interpolate to get the functional value to x_value
        '''
        i = self._find_segment(x_value)
        x_l, x_u = self.x_data[i], self.x_data[i + 1]
        y_l, y_u = self.y_data[i], self.y_data[i + 1]
        k_l, k_u = self.target[i], self.target[i + 1]
        d_x = x_u - x_l
        if degree == 1:
            return (k_u * (x_value - x_l) ** 2 \
                    - k_l * (x_u - x_value) ** 2) / (2 * d_x) \
                    + (y_u - y_l) / d_x - d_x / 6 * (k_u - k_l)
        elif degree == 2:
            return (k_u * (x_value - x_l) + k_l * (x_u - x_value)) / d_x
        else:
            return (k_u * (x_value - x_l) ** 3 \
                   + k_l * (x_u - x_value) ** 3) / (6 * d_x) \
                   + (y_l / d_x - d_x * k_l / 6) * (x_u - x_value) \
                   + (y_u / d_x - d_x * k_u / 6) * (x_value - x_l)

    def _find_segment(self, x_value):
        '''Using the bisection algorithm to find the lower index in the
        segment.
        :param x_value: x_value to place in segment defined by the x_data
        (instantiation)
        :return: The lower index in the segment
        '''
        i_left = 0
        i_right = len(self.x_data) - 1
        while True:
            if i_right - i_left <= 1:
                return i_left
            i = (i_right + i_left) / 2
            if x_value < self.x_data[i]:
                i_right = i
            else:
                i_left = i


class FinancialCubicSpline(NaturalCubicSpline):
    '''A financial cubic spline differs from the natural cubic spline in that
    has zero slope instead of zero curvature at the endpoint to the right.
    '''
    def __init__(self, x_data, y_data):
        x_data = DecimalVector(x_data)
        y_data = DecimalVector(y_data)
        assert len(x_data) == len(y_data), \
            'DecimalVectors are not of proper lengths'
        dimension = len(x_data)
        lower_diagonal = DecimalVector(dimension - 1, 0)
        diagonal = DecimalVector(dimension, 1)
        upper_diagonal = DecimalVector(dimension - 1, 0)
        target = DecimalVector(dimension, 0)
        d_x = x_data[1:] - x_data[0:-1]  # length = dimension-1
        d_y = y_data[1:] - y_data[0:-1]  # length = dimension-1
        # lower_diagonal[dimension-1] = 0
        lower_diagonal[0:dimension - 2] = d_x[0:-1]
        # diagonal[0] = diagonal[dimension] = 1
        diagonal[1:dimension - 1] = 2.0 * (d_x[1:] + d_x[0:-1])
        # upper diagonal[0] = 0
        upper_diagonal[1:dimension - 1] = d_x[1:dimension - 1]
        # target[0] = target[dimension] = 0
        target[1:dimension - 1] = 6.0 * (d_y[1:] / d_x[1:] \
                                - d_y[0:-1] / d_x[0:-1])
        lower_diagonal[-1] = d_x[-1]
        diagonal[-1] = Decimal('2') * d_x[-1]
        target[-1] = Decimal('-6.0') * d_y[-1] / d_x[-1]
        self.x_data = x_data
        self.y_data = y_data
        lu_decomp = LUdecomp3(lower_diagonal, diagonal, upper_diagonal)
        self.target = lu_decomp(target)

    def __str__(self):
        # __str__ is not defined at base function
        points = zip(self.x_data, self.y_data)
        return 'Financial cubic spline based on points:\n.. %s' % \
               '\n.. '.join(['(%.4f, %.4f)' % point for point in points])

    __repr__ = __str__


class PiecewiseConstant:
    '''A piecewise constant function is constant on intervals on the x-axis.
    It is right contionous as well which means that a set of points can define
    the function since each point is the right most point from the previous
    point.
    First point is assumed prolonged to x = minus infinity and last point is
    prolonged to x = infinity

    **At instantiation:**

    :param x_data: Array of x-coordinates
    :type x_data: A n-dimensional numpy array of float or decimal
    :param y_data: Array of y-coordinates
    :type y_data: A n-dimensional numpy array of float or decimal

    **When called as a function:**

    :param x: The value to interpolate from
    :type x: A real number

    **How to use:**

    >>> x_data = DecimalVector([1, 3, 5])
    >>> y_data = DecimalVector([7, 9, 13])
    >>> # Instantiation
    >>> pc = PiecewiseConstant(x_data, y_data)
    >>> pc
    Piecewise constant curve based on points:
    .. (1.0000, 7.0000)
    .. (3.0000, 9.0000)
    .. (5.0000, 13.0000)
    >>> pc([0, 1, 2, 3, 4, 5, 6])
    DecimalVector([7, 7, 9, 9, 13, 13, 13])
    '''
    def __init__(self, x_data, y_data):
        assert len(x_data) == len(y_data), \
            'DecimalVectors are not of proper lengths'
        self.x_data = DecimalVector(x_data)
        self.y_data = DecimalVector(y_data)

    def __str__(self):
        # __str__ is not defined at base function
        points = zip(self.x_data, self.y_data)
        return 'Piecewise constant curve based on points:\n.. %s' % \
               '\n.. '.join(['(%.4f, %.4f)' % p for p in points])
    __repr__ = __str__

    @_decimalvector_function(1)
    def __call__(self, x_value):
        '''
        :param x_value: x_value to place in segment defined by the x_data
        (instantiation)
        :return: The y_value of the upper point
        '''
        for x, y in zip(self.x_data, self.y_data):
            if x_value <= x:
                break
        return y


class LinearSpline:
    '''A linear interpolation connects point by the strait line though the
    points.
    First point is assumed prolonged horizontally to x = minus infinity and
    last
    point is likewise prolonged to x = infinity

    **At instantiation:**

    :param x_data: Array of x-coordinates
    :type x_data: A n-dimensional numpy array of float or decimal
    :param y_data: Array of y-coordinates
    :type y_data: A n-dimensional numpy array of float or decimal

    **When called as a function:**

    :param x: The value to interpolate from
    :type x: A real number

    **How to use:**

    >>> x_data = DecimalVector([1, 3, 5])
    >>> y_data = DecimalVector([7, 9, 13])
    >>> # Instantiation
    >>> li = LinearSpline(x_data, y_data)
    >>> li
    Linear interpolation curve based on points:
    .. (1.0000, 7.0000)
    .. (3.0000, 9.0000)
    .. (5.0000, 13.0000)
    >>> li([0, 1, 2, 3, 4, 5, 6])
    DecimalVector([7, 7, 8.0, 9, 11.0, 13, 13])
    '''
    def __init__(self, x_data, y_data):
        assert len(x_data) == len(y_data), \
            'DecimalVectors are not of proper lengths'
        self.x_data = DecimalVector(x_data)
        self.y_data = DecimalVector(y_data)

    def __str__(self):
        # __str__ is not defined at base function
        points = zip(self.x_data, self.y_data)
        return 'Linear interpolation curve based on points:\n.. %s' % \
               '\n.. '.join(['(%.4f, %.4f)' % p for p in points])
    __repr__ = __str__

    @_decimalvector_function(1)
    def __call__(self, x_value):
        '''
        :param x_value: x_value to place in segment defined by the x_data
                    (instantiation)
        :return: The y_value of the x_value according yo linear interpolation.
        '''
        if x_value > self.x_data[-1]:
            return self.y_data[-1]
        previous_x, previous_y = self.x_data[0] - 1, self.y_data[0]
        for x, y in zip(self.x_data, self.y_data):
            if x_value <= x:
                break
            previous_x, previous_y = x, y
        alfa = (x_value - previous_x) / (x - previous_x)
        return y * alfa + previous_y * (1 - alfa)


@_decimalvector_function(0)
def decimal_exp(x_value):
    '''The exponetial function as a DecimalVector function.

    **How to use**

    >>> x0 = 4
    >>> x1 = (1, float(2), Decimal('3'))
    >>> exp(x0)
    54.598150033144236
    >>> x1 = (1, float(2), Decimal('3'))
    >>> exp(x1)
    DecimalVector([2.71828182846, 7.38905609893, 20.0855369232])
    '''
    return Decimal.exp(x_value)


@_decimalvector_function(0)
def decimal_log(x_value):
    '''The natural logarithmic function as a DecimalVector function.

    **How to use**

    >>> log(8)
    2.0794415416798357
    >>> log((1, float(2), Decimal('8')))
    DecimalVector([0.0, 0.69314718056, 2.07944154168])
    '''
    return Decimal.ln(x_value)


def currency_format(value, currency='', places=2):
    '''Function to format a decimal value according to locale settings and the
    values of currency and places.

    :param value: Value to be displayed in locale setting with thousand
                    separator
    :type value: Decimal
    :param currency: suffix to be added output representing the unit of value
    :type currency: alphabetic string of length max 3
    :param places: number of decimals to be shown
    :type places: a positive integer
    :return: A string showing the formatted decimal value according to locale
             settings and the values of currency and places

    **How to use:**

    >>> currency_format(Decimal(1234567.4499999))
    '1.234.567,45'
    >>> currency_format(Decimal(1234567.4499999), 'DKK')
    '1.234.567,45 DKK'

    source: `Python Format Specification Mini-Language
    <http://docs.python.org/dev/library/string.html#formatspec>`_
    '''
    locale.setlocale(locale.LC_ALL, "")
    assert isinstance(value, Decimal), 'value must be a Decimal'
    assert (isinstance(currency, str)
              and len(currency) < 4
              and currency.isalpha()) if currency else True, \
              'currency must be an alphabetic string of length max 3'
    assert isinstance(places, int) and places > 0, \
              'places must be an positive integer'
    precision = Decimal(10) ** -places   # places = 2 --> q = Decimal('0.01')
    value = value.quantize(precision)    # round off to places decimals
    return '{:n} {}'.format(value, currency) if currency \
            else '{:n}'.format(value)


if __name__ == '__main__':
    import doctest
    doctest.testmod()