#
#  This file is part of the Connection-Set Algebra (CSA).
#  Copyright (C) 2010,2011 Mikael Djurfeldt
#
#  CSA is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  CSA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

class Function (object):
    def __neg__ (self):
        return GenericFunction (lambda i: - self (i))
    
    def __add__ (self, other):
        if not callable (other):
            return maybeAffine (other, 1.0, self)
        elif isinstance (other, (QuotedFunction, AffineFunction)):
            return other.__add__ (self)
        elif isinstance (other, GenericFunction):
            return GenericFunction (lambda i: self (i) + other.function (i))
        else:
            return GenericFunction (lambda i: self (i) + other (i))

    def __radd__ (self, other):
        return self.__add__ (other)

    def __sub__ (self, other):
        return self.__add__ (- other)

    def __rsub__ (self, other):
        return self.__neg__ ().__add__ (other)

    def __mul__ (self, other):
        if not callable (other):
            return maybeAffine (0.0, other, self)
        elif isinstance (other, (QuotedFunction, AffineFunction)):
            return other.__mul__ (self)
        elif isinstance (other, GenericFunction):
            return GenericFunction (lambda i: self (i) * other.function (i))
        else:
            return GenericFunction (lambda i: self (i) * other (i))

    def __rmul__ (self, other):
        return self.__mul__ (other)


class QuotedFunction (Function):
    def __init__ (self, expression):
        self.expression = expression

    def __call__ (self, i):
        return self.expression

    def __neg__ (self):
        return QuotedFunction (- self.expression)
    
    def __add__ (self, other):
        if not callable (other):
            return QuotedFunction (self.expression + other)
        elif isinstance (other, QuotedFunction):
            return QuotedFunction (self.expression + other.expression)
        elif isinstance (other, AffineFunction):
            return other.__add__ (self)
        else:
            return maybeAffine (self.expression, 1.0, other)

    def __mul__ (self, other):
        if not callable (other):
            return QuotedFunction (self.expression * other)
        elif isinstance (other, QuotedFunction):
            return QuotedFunction (self.expression * other.expression)
        elif isinstance (other, AffineFunction):
            return other.__mul__ (self)
        else:
            return maybeAffine (0.0, self.expression, other)        


class GenericFunction (Function):
    def __init__ (self, function):
        self.function = function

    def __call__ (self, i):
        return self.function (i)

    def __neg__ (self):
        return GenericFunction (lambda i: - self.function (i))

    def __add__ (self, other):
        if not callable (other):
            return maybeAffine (other, 1.0, self.function)
        elif isinstance (other, (QuotedFunction, AffineFunction)):
            return other.__add__ (self)
        elif isinstance (other, GenericFunction):
            return GenericFunction (lambda i: self.function (i) + other.function (i))
        else:
            return GenericFunction (lambda i: self.function (i) + other (i))

    def __mul__ (self, other):
        if not callable (other):
            return maybeAffine (0.0, other, self.function)
        elif isinstance (other, (QuotedFunction, AffineFunction)):
            return other.__mul__ (self)
        elif isinstance (other, GenericFunction):
            return GenericFunction (lambda i: self.function (i) * other.function (i))
        else:
            return GenericFunction (lambda i: self.function (i) * other (i))


class AffineFunction (Function):
    def __init__ (self, constant, coefficient, function):
        self.const = constant
        self.coeff = coefficient
        self.func = function

    def __call__ (self, i):
        return self.const + self.coeff * self.func (i)

    def __neg__ (self):
        return maybeAffine (- self.const, - self.coeff, self.func)
    
    def __add__ (self, other):
        if not callable (other):
            return maybeAffine (self.const + other, self.coeff, self.func)
        elif isinstance (other, QuotedFunction):
            return maybeAffine (self.const + other.expression,
                                self.coeff, self.func)
        elif isinstance (other, AffineFunction):
            f = lambda i: \
                    self.const * self.func (i) \
                    + other.const * other.func (i)
            return maybeAffine (self.const + other.const,
                                1.0,
                                f)

    def __mul__ (self, other):
        if not callable (other):
            return maybeAffine (self.const * other,
                                self.coeff * other,
                                self.func)
        elif isinstance (other, QuotedFunction):
            return maybeAffine (self.const * other.expression,
                                self.coeff * other.expression,
                                self.func)
        elif isinstance (other, AffineFunction):
            f = lambda i: \
                    other.const * self.coeff * self.func (i) \
                    + self.const * other.coeff * other.func (i) \
                    + self.coeff * other.coeff \
                      * self.func (i) * other.func (i)
            return maybeAffine (self.const * other.const,
                                1.0,
                                f)

def maybeAffine (const, coeff, func):
    if coeff == 0.0:
        return QuotedFunction (const)
    elif const == 0.0 and coeff == 1.0:
        return GenericFunction (func)
    else:
        return AffineFunction (const, coeff, func)
