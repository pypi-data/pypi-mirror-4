############################
decimalpy - long description
############################

In financial calculations it is recommended to use Decimal as a numerical base.
At the same time there is a need to have the same functionality as in `numpy <http://numpy.scipy.org>`_ or `R <http://www.r-project.org>`_.
So the goal of this package is to fill this gap, i.e. implementing Decimal based
structures to ease eg. financial calculations. 

In the creation of the `finance <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#the-finance-package>`_ package. it was decided to use Decimal
based structures.

There were 2 reasons for this:

#. In finance decimals matters and when other financial systems use the IEEE
   standard 854-1987 the package finance need to do the same
#. For valuation purposes it is important that the financial calculations are
   the exact same as those performed in eg spreadsheets who use the IEEE
   standard 854-1987 

`See also the chapter that examplifies the reasons for this. <http://www.bruunisejs.dk/PythonHacks/rstFiles/600%20On%20Python.html#arrays-for-financial-calculations>`_.

After a while it was clear that there were a lot of code with a life or purpose of
its own. And that was how the decimalpy package was born.

The Package `decimalpy <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#the-decimalpy-package-for-python>`_ is inspired by `numpy <http://numpy.scipy.org>`_ and eg the vector concept of `The R package <http://www.r-project.org>`_.
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
`finance <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#the-finance-package>`_ .

The decimal package is open source under the `Python Software Foundation
License <http://www.opensource.org/licenses/PythonSoftFoundation.php>`_

How to install
--------------

Just run setup.py install command. Or in windows use the windows installer.

Documentation, etc
------------------

Visit my `homepage <http://www.bruunisejs.dk/PythonHacks/>`_ to see more on how 
to use and the research behind the code. It's a blog like place on finance, math 
and scientific computing.

######################
Planned added contents
######################

The planned development so far is:

Planned added content of version 0.2:
    Implementation of matrix and more decimalbased functions
    
Planned added content of version 0.3:
    Implementation af a statistical test package
