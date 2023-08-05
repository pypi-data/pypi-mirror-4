#
#   Copyright 2011 Olivier Kozak
#
#   This file is part of Mocki.
#
#   Mocki is free software: you can redistribute it and/or modify it under the
#   terms of the GNU Lesser General Public License as published by the Free
#   Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   Mocki is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
#   details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with Mocki. If not, see <http://www.gnu.org/licenses/>.
#

"""Several convenient stubs.

"""
def returnValue(value):
    """Returns a given value on invocation to the matching calls.

    This is a shortcut to ReturnValueStub.

    """
    return ReturnValueStub(value)

class ReturnValueStub(object):
    """Returns a given value on invocation to the matching calls.

    To use it, first instanciate a mock, then stub it to return a given value on
    invocation to the given matching calls :
        >>> from mocki import Mock
        >>> from mocki.matchers import anyCall

        >>> mock = Mock('theMock')

        >>> mock.on(anyCall()).then(returnValue('value'))

    Now, any matching invocation will return this given value :
        >>> mock()
        'value'

    """
    def __init__(self, value):
        self.value = value

    def __call__(self, call):
        return self.value

    def __repr__(self):
        """This stub's representation :
            >>> stub = returnValue('value')

            >>> repr(stub)
            "returnValue('value')"

        """
        return '%s(%r)' % (returnValue.__name__, self.value)

def raiseException(exception):
    """Raises a given exception on invocation to the matching calls.

    This is a shortcut to RaiseExceptionStub.

    """
    return RaiseExceptionStub(exception)

class RaiseExceptionStub(object):
    """Raises a given exception on invocation to the matching calls.

    To use it, first instanciate a mock, then stub it to raise a given exception
    on invocation to the given matching calls :
        >>> from mocki import Mock
        >>> from mocki.matchers import anyCall

        >>> mock = Mock('theMock')

        >>> mock.on(anyCall()).then(raiseException(Exception('error')))

    Now, any matching invocation will raise this given exception :
        >>> mock()
        Traceback (most recent call last):
        ...
        Exception: error

    """
    def __init__(self, exception):
        self.exception = exception

    def __call__(self, call):
        raise self.exception

    def __repr__(self):
        """This stub's representation :
            >>> stub = raiseException(Exception('error'))

            >>> repr(stub)
            "raiseException(Exception('error',))"

        """
        return '%s(%r)' % (raiseException.__name__, self.exception)

def inOrder(stub, *stubs):
    """Describes a sequence of stubs that will be used in order. Each stub will
    be used sequentially, for each invocation to the matching calls, the last
    stub being repeatedly used on any further matching invocation.

    This is a shortcut to InOrderStub.

    """
    return InOrderStub(stub, *stubs)

class InOrderStub(object):
    """Describes a sequence of stubs that will be used in order. Each stub will
    be used sequentially, for each invocation to the matching calls, the last
    stub being repeatedly used on any further matching invocation.

    To use it, first instanciate a mock, then stub it to follow a given sequence
    of stubs on invocation to the given matching calls :
        >>> from mocki import Mock
        >>> from mocki.matchers import anyCall

        >>> mock = Mock('theMock')

        >>> mock.on(anyCall()).then(inOrder(returnValue('value'), returnValue('otherValue')))

    Now, the 1st matching invocation will use the 1st stub and the 2nd matching
    invocation will use the 2nd stub, this last stub being repeatedly used on
    any further matching invocation :
        >>> mock()
        'value'

        >>> mock()
        'otherValue'

        >>> mock()
        'otherValue'

    """
    def __init__(self, stub, *stubs):
        self.allStubs = [stub] + list(stubs)

        self.currentStubIter = iter(self.allStubs)
        self.lastStub = self.allStubs[-1]

    def __call__(self, call):
        try:
            return next(self.currentStubIter)(call)
        except StopIteration:
            return self.lastStub(call)

    def __repr__(self):
        """This stub's representation :
            >>> stub = inOrder(returnValue('value'), returnValue('otherValue'))

            >>> repr(stub)
            "inOrder(returnValue('value'), returnValue('otherValue'))"

        """
        def getAllStubsAsCsv():
            return ', '.join(map(repr, self.allStubs))

        return '%s(%s)' % (inOrder.__name__, getAllStubsAsCsv())
