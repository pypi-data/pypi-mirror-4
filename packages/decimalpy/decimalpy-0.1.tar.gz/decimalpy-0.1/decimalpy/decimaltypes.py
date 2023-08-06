#############################################################################
# The finance package is open source under the `Python Software Foundation  #
# License <http://www.opensource.org/licenses/PythonSoftFoundation.php>`_   #
#############################################################################

'''
**The decimalpy.decimaltypes**

This module contains the Decimal subtype DecimalVector and the decorator
decimalvector_function that converts a simple function into a DecimalVector
function ie a function that can handle and return a DecimalVector.

Finally the module contains a base class for a Decimal valued dictionary with
sorted keys.
'''
from decimal import Decimal
#from decimalmetafunctions import DecimalSolver
from mathematical_meta_code import CummutativeAddition, \
                                   CummutativeMultiplication, Power
from decimalmetafunctions import decimal_simple_poly_exponent, \
                                 to_decimal, \
                                 to_integer, \
                                 decimal_division, \
                                 DecimalSolver


def validate_decimalvector_arguments(function_object):
    '''Decorator to transform second argument into a DecimalVector if
    necessary.
    If a part of the second argument can't be transformed into a Decimal
    number then it get's the value None.

    **How to use:**

    >>> @validate_decimalvector_arguments
    ... def f(x, y):
    ...     return x, y
    ...
    >>> f('test', (1, float(2), Decimal('3'), 'text'))
    ('test', [Decimal('1'), Decimal('2.0'), Decimal('3'), None])
    '''
    def wrap(arg1, arg2):
        '''wrap is called between function and arguments
        '''
        if isinstance(arg2, (int, float, Decimal)):
            new_arg2 = len(arg1) * [to_decimal(arg2)]
        elif isinstance(arg2, (tuple, list)):
            assert any(isinstance(val, (int, float, Decimal)) for val in
                            arg2), 'list must be list of numbers'
            new_arg2 = [to_decimal(val) for val in arg2]
        elif isinstance(arg2, DecimalVector):
            new_arg2 = arg2
        return function_object(arg1, new_arg2)
    return wrap


def decimalvector_function(variable_index, argument_is_decimal=False):
    '''A decorator to convert python functions to numpy universal functions

    A standard function of 1 variable is extended by a decorator to handle
    all values in a list, tuple or numpy array

    :param variable_index: Specifies index for args to use as variable.
        This way the function can be used in classes as well as functions
    :type variable_index: An positive integer

    **How to use:**

    In the example below decimalvector_function is used on the first
    parameter x:

    >>> @decimalvector_function(0)
    ... def test(x, y=2):
    ...     return x+y
    ...
    >>> x0 = 4
    >>> x1 = (1, float(2), Decimal('3'))
    >>> x2 = [2, 3, 4]
    >>> x3 = DecimalVector(x1) + 2
    >>> test(x0)
    Decimal('6')
    >>> print test(x1)
    DecimalVector([3, 4.0, 5])
    >>> print test(x2)
    DecimalVector([4, 5, 6])
    >>> print test(x3)
    DecimalVector([5, 6.0, 7])

    Note that since argument y has a default value 2 it isn't set in the
    function call. So these are not handled by the decimalvector_function.
    To see this do:

    >>> @decimalvector_function(1)
    ... def test(x, y=2):
    ...     return x+y
    ...
    >>> try:
    ...     test(1)
    ... except Exception, error_tekst:
    ...     print error_tekst
    ...
    tuple index out of range
    * variable_index=1
    * args=(1,)
    * kwargs={}
    * argument_is_decimal=False

    In the example above args is a tuple of length 1, we want's to let the
    decimalvector_function work on argument number 2 at position 1, but
    there are no argument number 2 in the call.

    However the call below works just fine:

    >>> test(1, (1, float(2), Decimal('3')))
    DecimalVector([2, 3.0, 4])

    It is just that the value has to be set in the function call in order to
    have decimalvector_function working.
    Therefore setting a default value make's no sense.

    If argument_is_decimal is True it means that the argument is transformed
    into a Decimal if possible  else the value is returned.

    >>> @decimalvector_function(0)
    ... def test(x):
    ...     return 2/x
    ...
    >>> test(3)
    Decimal('0')

    Here the division becomes integer part division since the argument is an
    integer and hence both nominator and denominator are integers.

    If on the other hand argument_is_decimal is True the argument becomes a
    Decimal and division becomes division between real numbers as shown
    below:

    >>> @decimalvector_function(0, True)
    ... def test(x):
    ...     return 2/x
    ...
    >>> test(3)
    Decimal('0.6666666666666666666666666667')

    Remember that arguments at instantiation must be decimals. Hence use of
    the function to_decimal in __init__

    >>> from decimalpy import to_decimal
    >>> class Test:
    ...     def __init__(self, x):
    ...         self.x = to_decimal(x)
    ...     @decimalvector_function(1, True)
    ...     def __call__(self, y):
    ...        return self.x * y
    ...
    >>> test = Test(2.)
    >>> test([3., 6, 9])
    DecimalVector([6.00, 12.0, 18.0])
    '''
    def wrap(func):
        '''Function to wrap around methods and functions
        '''
        def wrap_func(*args, **kwargs):
            '''Function specifying that input and output is decimal.
            '''
            try:
                if len(args) >= variable_index:
                    before = list(args[:variable_index])
                    arguments = args[variable_index]
                    after = list(args[variable_index + 1:])
                    validate = lambda x: Decimal('%s' % x) \
                                if argument_is_decimal else x
                    if isinstance(arguments, (list, tuple, DecimalVector)):
                        return DecimalVector([func(*(before
                                                     + [validate(x)]
                                                     + after)
                                                     )
                                            for x in arguments
                                            ])
                    elif isinstance(arguments, (int, float, Decimal)):
                        return Decimal('%s' % func(*(before
                                                     + [validate(arguments)]
                                                     + after))
                                       )
            except Exception, error_text:
                raise Exception('%s\n* variable_index=%s\n' \
                                '* args=%s\n' \
                                '* kwargs=%s\n' \
                                '* argument_is_decimal=%s'
                                % (error_text,
                                   variable_index,
                                   args,
                                   kwargs,
                                   argument_is_decimal
                                   )
                                )
            return Decimal('%s' % func(*args))
        wrap_func.__name__ = func.__name__
        wrap_func.__doc__ = func.__doc__
        return wrap_func
    return wrap


class DecimalVector(CummutativeAddition,
                    CummutativeMultiplication,
                    Power,
                    list
                    ):
    '''An abstract datatype integrating the qualities of numpy's array
    and the class decimal.

    **How to use**

    >>> cf = DecimalVector(5, 0.1)
    >>> cf[-1] += 1
    >>> cf
    DecimalVector([0.1, 0.1, 0.1, 0.1, 1.1])
    >>> times = DecimalVector(range(1,6))
    >>> discount = Decimal('1.1') ** - times
    >>> sum(discount * cf) # Present value
    Decimal('1.000000000000000000000000000')
    >>> discount(cf) # Present value by dot product
    Decimal('1.000000000000000000000000000')
    >>> sum(cf * Decimal('1.1') ** - times) # Present value
    Decimal('1.000000000000000000000000000')
    >>> cf(Decimal('1.1') ** - times) # Present value by dot product
    Decimal('1.000000000000000000000000000')
    >>> sum(cf / Decimal('1.1') ** times) # Present value
    Decimal('1.000000000000000000000000000')
    >>> times[:4] - times[1:]
    DecimalVector([-1, -1, -1, -1])
    '''
    def __init__(self, tuple_or_length, default=1):
        if isinstance(tuple_or_length, int) and tuple_or_length > 0:
            list.__init__(self, [to_decimal(default)] * tuple_or_length)
        elif isinstance(tuple_or_length, (tuple, list)):
            list.__init__(self, [to_decimal(val) for val in tuple_or_length])
        elif tuple_or_length.__class__.__name__ == 'DecimalVector':
            self = tuple_or_length
        else:
            list.__init__(self, [])

    def __str__(self):
        return 'DecimalVector([%s])' % ', '.join([str(x) for x in self])

    def __call__(self, d_vector):  # Vector dot product
        '''Vector dot product can be considered as a function with rhs of the
        dot as the argument whereas the lhs is the "matrix"
        '''
        return sum(self * d_vector)

    __repr__ = __str__

    def __getslice__(self, start, stop):
        return DecimalVector(list.__getslice__(self, start, stop))

    def __setitem__(self, key, value):
        list.__setitem__(self, key, to_decimal(value))

    def __setslice__(self, start, stop, values):
        list.__setslice__(self, start, stop, DecimalVector(values))

    def __neg__(self):
        return DecimalVector([-1 * x for x in self])

    def __abs__(self):
        return DecimalVector([abs(x) for x in self])

    @validate_decimalvector_arguments
    def __add__(self, d_vector):
        return DecimalVector([x + y for x, y in zip(self, d_vector)])

    @validate_decimalvector_arguments
    def __mul__(self, d_vector):
        return DecimalVector([x * y for x, y in zip(self, d_vector)])

    @validate_decimalvector_arguments
    def __div__(self, d_vector):
        return DecimalVector([x / y for x, y in zip(self, d_vector)])

    @validate_decimalvector_arguments
    def __rdiv__(self, d_vector):
        return DecimalVector([x / y for x, y in zip(d_vector, self)])

    @validate_decimalvector_arguments
    def __pow__(self, d_vector):
        return DecimalVector([x ** y for x, y in zip(self, d_vector)])

    @validate_decimalvector_arguments
    def __rpow__(self, d_vector):
        return DecimalVector([x ** y for x, y in zip(d_vector, self)])


class SortedKeysDecimalValuedDict(CummutativeAddition,
                                  CummutativeMultiplication,
                                  dict
                                  ):
    '''SortedKeysDecimalValuedDict is a generalisation of DecimalVector. The
    later is a SortedKeysDecimalValuedDict where the keys are consequtive
    integers starting with zero.

    In SortedKeysDecimalValuedDict the keys can be any ordered set of elements
    of the same type.

    The values are off course still Decimals. And the vectorlike functionality
    is still valid if the keys are of the same type.

    Arguments at instantiation should be:

    * a SortedKeysDecimalValuedDict
    * a DecimalVector
    * a dictionary where the values are decimals
    * a list of pairs of key and value. Values are of type Decimals ??

    The type setting of keys can be defined at the static method
    __validate_key__ which has to return an validated value if possible.
    Otherwise it has to return the value None.

    So to create a SortedKeysDecimalValuedDict with keys converted to strings
    eg just do:

    >>> class string_based_decimalvector(SortedKeysDecimalValuedDict):
    ...     @staticmethod
    ...     def __validate_key__(key):
    ...         return str(key)

    Now any attempted key is converted to it's string representation.


    **How to use**

    >>> class TimeFlow(SortedKeysDecimalValuedDict):
    ...     @staticmethod
    ...     def __validate_key__(key):
    ...         return SortedKeysDecimalValuedDict.__validate_value__(key)
    ...

    >>> cf = TimeFlow(DecimalVector(5, 0.1))
    >>> cf[4] += 1 # This is not the index 4, but the key 4
    >>> cf
    Data for the TimeFlow:
    * key: 0, value: 0.1
    * key: 1, value: 0.1
    * key: 2, value: 0.1
    * key: 3, value: 0.1
    * key: 4, value: 1.1

    >>> times = TimeFlow(DecimalVector(range(1,6)))
    >>> -times
    Data for the TimeFlow:
    * key: 0, value: -1
    * key: 1, value: -2
    * key: 2, value: -3
    * key: 3, value: -4
    * key: 4, value: -5
    >>> discount = Decimal('1.1') ** - times
    >>> discount
    Data for the TimeFlow:
    * key: 0, value: 0.9090909090909090909090909091
    * key: 1, value: 0.8264462809917355371900826446
    * key: 2, value: 0.7513148009015777610818933133
    * key: 3, value: 0.6830134553650706918926302848
    * key: 4, value: 0.6209213230591551744478457135
    >>> present_values = discount * cf
    >>> sum(present_values.values()) # Present value
    Decimal('1.000000000000000000000000000')
    '''
    def __init__(self, init_arg={}, reverse=False):
        self.reverse = reverse
        pairs = []
        if isinstance(init_arg, self.__class__):
            pairs = init_arg.iteritems()
        elif isinstance(init_arg, dict):
            pairs = init_arg.iteritems()
        elif isinstance(init_arg, DecimalVector):
            l = len(init_arg) + 1
            pairs = zip(range(l), init_arg)
        outdict = {}
        for key, value in pairs:
            key = self.__validate_key__(key)
            value = self.__validate_value__(value)
            if key != None and value != None:
                outdict[key] = value
        dict.__init__(self,  outdict)

    @staticmethod
    def __validate_key__(key):
        raise NotImplementedError(
                '__validate_key__ must always be implemented'
                )

    @staticmethod
    def __validate_value__(value):
        return to_decimal(value)

    def keys(self):
        return sorted(dict.keys(self), reverse=self.reverse)

    def values(self):
        return DecimalVector([self[key] for key in self.keys()])

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def iterkeys(self):
        for key in self.keys():
            yield key

    def itervalues(self):
        for key in self.keys():
            yield self[key]

    def iteritems(self):
        for key in self.keys():
            yield (key, self[key])

    def last_key(self):
        return self.keys()[-1]

    def first_key(self):
        return self.keys()[0]

    def __getitem__(self,  key):
        if isinstance(key, slice):
            # slice = [key.start, key.stop]
            if key.start == None:
                first_key = self.first_key()
            else:
                first_key = self.__validate_key__(key.start)
            if key.stop == None:
                last_key = self.last_key()
            else:
                last_key = self.__validate_key__(key.stop)
            if first_key and last_key and first_key <= last_key:
                dct = dict([(key, value) for key, value in self.items()
                        if first_key <= key <= last_key
                        ])
                return self.__class__(dct, reverse=self.reverse)
            else:
                return self.__class__({}, reverse=self.reverse)
        elif self.__validate_key__(key) in self.keys():
            return dict.__getitem__(self,  self.__validate_key__(key))

    def __setitem__(self,  key,  value):
        key = self.__validate_key__(key)
        value = self.__validate_value__(value)
        if key != None and value != None:
            dict.__setitem__(self,  key,  value)

    def __str__(self):
        content = '\n* '.join(sorted(['key: %s, value: %s' % (key, value)
                                    for key, value in self.items()]))
        return 'Data for the %s:\n* %s' % (self.__class__.__name__, content)

    __repr__ = __str__

    def __add__(self, value):
        out = self.__class__(self)
        if isinstance(value, self.__class__):
            for key in value.keys():
                if key in out.keys():
                    out[key] += value[key]
                else:
                    out[key] = value[key]
        else:
            value = self.__validate_value__(value)
            if value:
                for key in out.keys():
                    out[key] += value
        return out

    def __mul__(self, value):
        out = self.__class__(self)
        if isinstance(value, self.__class__) and self.keys() == value.keys():
            # multiplication with a SortedKeysDecimalValuedDict is not
            # possible unless same set of keys
            for key in out.keys():
                out[key] *= value[key]
        else:
            value = self.__validate_value__(value)
            if value:
                for key in out.keys():
                    out[key] *= value
        return out

    def __neg__(self):
        out = self.__class__(self)
        for key in out.keys():
            out[key] *= Decimal('-1')
        return out

    def __abs__(self):
        out = self.__class__(self)
        for key in self.keys():
            out[key] = abs(self[key])
        return out

    def __rsub__(self, value):
        out = self.__class__(self)
        if isinstance(value, self.__class__):
            for key in self.keys():
                if key in value.keys():
                    out[key] -= self[key]
                else:
                    out[key] = -self[key]
        else:
            value = self.__validate_value__(value)
            if value:
                for key in self.keys():
                    out[key] = value - self[key]
        return out

    def __div__(self, value):
        out = self.__class__(self)
        if (isinstance(value, self.__class__)
          and self.keys() == value.keys()):
            for key in self.keys():
                out[key] = decimal_division(self[key], value[key])
        else:
            value = self.__validate_value__(value)
            if value:
                for key in self.keys():
                    out[key] = decimal_division(self[key], value)
        return out

    def __rdiv(self, value):
        out = self.__class__(self)
        if (isinstance(value, self.__class__)
          and self.keys() == value.keys()):
            for key in self.keys():
                out[key] = decimal_division(self[key], value[key])
        else:
            value = self.__validate_value__(value)
            if value:
                for key in self.keys():
                    out[key] = decimal_division(self[key], value)
        return out

    def __pow__(self, value):
        out = self.__class__(self)
        if (isinstance(value, self.__class__)
          and self.keys() == value.keys()):
            for key in self.keys():
                out[key] = decimal_simple_poly_exponent(self[key], value[key])
        else:
            value = self.__validate_value__(value)
            if value:
                for key in self.keys():
                    out[key] = decimal_simple_poly_exponent(self[key], value)
        return out

    def __rpow__(self, value):
        out = self.__class__(self)
        if (isinstance(value, self.__class__)
          and self.keys() == value.keys()):
            for key in self.keys():
                out[key] = decimal_simple_poly_exponent(value[key], self[key])
        else:
            value = self.__validate_value__(value)
            if value != None:
                for key in self.keys():
                    out[key] = decimal_simple_poly_exponent(value, self[key])
        return out


class PolyExponents(SortedKeysDecimalValuedDict):
    '''PolyExponents are an extension of polynomials.
    Here the exponents doesn't have to be just integers.
    All decimal type values are accepted as exponents.
    So it is fair to say that a PolyExponents is a linear combination of
    roots, negative and positive powers.

    It uses an extended Horners method for evaluation.
    And derivatives can found exact by specifying a degree of differention.

    The price paid for this extension is that PolyExponents can only have
    positive arguments.

    **At instantiation:**

    :param dct_of_exponents_and_factors: Array of x-coordinates
    :type dct_of_exponents_and_factors: A dictionary where the keys
        are exponents and the values are factors.

    **When called as a function**

    :param base_value: Specifying the degree of differention
    :type base_value: A number (Integer, float or Decimal)
    :return: When called as a function returns the functional value.
        If a degree is specified then the degree order derivative is returned

    **How to use:**

    Let's start with a simple polynomial: :math:`p(x)=x^2 + 2 \cdot x + 2`.
    Then the dct_of_exponents_and_factors is {2:1, 1:2, 0:2}.
    The dct_of_exponents_and_factors of the first derivative is {1:2, 0:2}.
    And the dct_of_exponents_and_factors of the first derivative is {0:2}.

    Instantiation is done as:

    >>> pe = PolyExponents({2:1, 1:2, 0:2})
    >>> print pe
    Data for the PolyExponents:
    * exponent: 0, factor: 2
    * exponent: 1, factor: 2
    * exponent: 2, factor: 1

    >>> pe
    pe(x) =  + 1 * x^2 + 2 * x^1 + 2

    >>> pe.derivative()
    pe(x) =  + 2 * x^1 + 2

    >>> pe.derivative().derivative()
    pe(x) =  + 2

    >>> -pe
    pe(x) =  - 1 * x^2 - 2 * x^1 - 2

    >>> PolyExponents({})
    pe(x) =  + 0

    >>> pe * 2
    pe(x) =  + 2 * x^2 + 4 * x^1 + 4

    >>> pe + pe
    pe(x) =  + 2 * x^2 + 4 * x^1 + 4

    >>> pe * pe
    pe(x) =  + 1 * x^4 + 4 * x^3 + 8 * x^2 + 8 * x^1 + 4

    >>> pe ** 2
    pe(x) =  + 1 * x^4 + 4 * x^3 + 8 * x^2 + 8 * x^1 + 4

    >>> PolyExponents({1:1, 0:1}) ** 5
    pe(x) =  + 1 * x^5 + 5 * x^4 + 10 * x^3 + 10 * x^2 + 5 * x^1 + 1

    Get function value, first order derivative and second order derivative at
    x = 1:

    >>> pe(1), pe.derivative()(1), pe.derivative().derivative()(1)
    (Decimal('5'), Decimal('4'), Decimal('2'))

    >>> try:
    ...     pe(-1)
    ... except Exception, error_text:
    ...     print error_text
    Only non-negative arguments are allowed
    * variable_index=1
    * args=(pe(x) =  + 1 * x^2 + 2 * x^1 + 2, -1)
    * kwargs={}
    * argument_is_decimal=False

    >>> pe = PolyExponents({1:1, 0:1}) ** 3
    >>> pe(2)
    Decimal('27')
    >>> pe.inverse(27)
    Decimal('2.000000000000000000000000000')

    >>> pe = PolyExponents({2:1, 1:1}) ** 2
    >>> pe(2)
    Decimal('36')

    >>> pe = PolyExponents({-1:1, -2:1, 1:2})
    >>> pe
    pe(x) =  + 2 * x^1 + 1 * x^-1 + 1 * x^-2
    >>> pe(2)
    Decimal('4.75')
    >>> pe = PolyExponents({-1:-1})
    >>> pe(2)
    Decimal('-0.5')
    '''
    def __init__(self, exponents_and_factors):
        if exponents_and_factors == {}:
            exponents_and_factors = {0: 0}
        SortedKeysDecimalValuedDict.__init__(self,
                                             exponents_and_factors,
                                             True
                                             )

    @staticmethod
    def __validate_key__(value):
        return to_decimal(value)

    def __str__(self):
        content = '\n* '.join(['exponent: %s, factor: %s' % (key, value)
                                for key, value in sorted(self.items())])
        return 'Data for the %s:\n* %s' % (self.__class__.__name__, content)

    def to_latex(self, reverse=True):
        get_sign = lambda nbr: '+' if nbr >= 0 else '-'
        out = ''
        for exponent, factor in sorted(self.items(), reverse=reverse):
            sign = get_sign(factor)
            if exponent:
                out += ' %s %s * x^%s' % (sign, abs(factor), exponent)
            else:
                out += ' %s %s' % (sign, abs(factor))
        return 'pe(x) = %s' % out

    __repr__ = to_latex

    @decimalvector_function(1)
    def __call__(self, base_value):
        base_value = PolyExponents.__validate_value__(base_value)
        assert base_value >= 0, 'Only non-negative arguments are allowed'
        exponent1, factor = self.items()[0]
        if len(self.items()) == 1:
            return decimal_simple_poly_exponent(base_value,
                                                exponent1,
                                                factor
                                                )
        for exponent2, addend in self.items()[1:]:
            factor = decimal_simple_poly_exponent(base_value,
                                                  exponent1 - exponent2,
                                                  factor,
                                                  addend
                                                  )
            exponent1 = exponent2
        if exponent2 != Decimal('0'):
            factor = decimal_simple_poly_exponent(base_value,
                                                  exponent2,
                                                  factor
                                                  )
        return factor

    def __mul__(self, value):
        if isinstance(value, self.__class__):
            out = self.__class__({})
            for self_key in self.keys():
                for value_key in value.keys():
                    new_key = self_key + value_key
                    new_value = self[self_key] * value[value_key]
                    if new_key in out:
                        out[new_key] += new_value
                    else:
                        out[new_key] = new_value
        else:
            out = self.__class__(self)
            value = self.__validate_value__(value)
            if value:
                for key in out.keys():
                    out[key] *= value
        return out

    def __div__(self, value):
        out = self.__class__(self)
        value = self.__validate_value__(value)
        if value:
            for key in self.keys():
                out[key] = decimal_division(self[key], value)
        return out

    def __rdiv(self, value):
        out = self.__class__(self)
        value = self.__validate_value__(value)
        if value:
            for key in self.keys():
                out[key] = decimal_division(self[key], value)
        return out

    def __pow__(self, value):

        def local_power(root, exponent):
            if exponent == 1:
                return root
            elif exponent % 2:
                return local_power(root, exponent - 1) * root
            else:
                return local_power(root * root, exponent / 2)

        out = self.__class__(self)
        value = to_integer(value)
        if value and value > 0:
            if out == self.__class__({}):
                return self.__class__({0: 1})
            else:
                return local_power(out, value)

    def __rpow__(self, value):
        pass

    def derivative(self):
        out = self.__class__({})
        for exponent, factor in self.__class__(self).items():
            if exponent != Decimal('0'):
                out[exponent - 1] = exponent * factor
        return out

    def inverse(self,
                value,
                minimum=Decimal('0'),  # Or start value
                maximum=None,
                precision=Decimal('1e-20'),
                max_iteration=30
                ):
        value = self.__validate_value__(value)
        if value:
            f = lambda x: self.__call__(x)
            df = lambda x: self.derivative()(x)
            root = DecimalSolver(f, df, precision, max_iteration)
            return root(value, minimum, maximum)

if __name__ == '__main__':
    import doctest
    doctest.testmod()