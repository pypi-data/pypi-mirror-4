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

"""Several convenient expectations.

"""
def atLeast(nTimes):
    """Returns true if the matching calls were invoked at least N times.

    This is a shortcut to AtLeastExpectation.

    """
    return AtLeastExpectation(nTimes)

class AtLeastExpectation(object):
    """Returns true if the matching calls were invoked at least N times.

    To use it, first instanciate a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked at least 1 time :
        >>> from mocki.matchers import anyCall

        >>> mock.verify(anyCall()).invoked(atLeast(1))
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    With one call invoked :
        >>> mock('1stCall')

        >>> mock.verify(anyCall()).invoked(atLeast(1))

    With 2 calls invoked :
        >>> mock('2ndCall')

        >>> mock.verify(anyCall()).invoked(atLeast(1))

    """
    def __init__(self, nTimes):
        self.nTimes = nTimes

    def __call__(self, calls):
        return len(calls) >= self.nTimes

    def __repr__(self):
        """This expectation's representation :
            >>> expectation = AtLeastExpectation(1)

            >>> repr(expectation)
            'atLeast(1)'

        """
        return '%s(%r)' % (atLeast.__name__, self.nTimes)

def atLeastOnce():
    """Returns true if the matching calls were invoked at least once.

    This is a shortcut to AtLeastOnceExpectation.

    """
    return AtLeastOnceExpectation()

class AtLeastOnceExpectation(object):
    """Returns true if the matching calls were invoked at least once.

    To use it, first instanciate a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked at least once :
        >>> from mocki.matchers import anyCall

        >>> mock.verify(anyCall()).invoked(atLeastOnce())
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    With one call invoked :
        >>> mock('1stCall')

        >>> mock.verify(anyCall()).invoked(atLeastOnce())

    With 2 calls invoked :
        >>> mock('2ndCall')

        >>> mock.verify(anyCall()).invoked(atLeastOnce())

    """
    def __call__(self, calls):
        return len(calls) >= 1

    def __repr__(self):
        """This expectation's representation :
            >>> expectation = AtLeastOnceExpectation()

            >>> repr(expectation)
            'atLeastOnce()'

        """
        return '%s()' % atLeastOnce.__name__

def atMost(nTimes):
    """Returns true if the matching calls were invoked at most N times.

    This is a shortcut to AtMostExpectation.

    """
    return AtMostExpectation(nTimes)

class AtMostExpectation(object):
    """Returns true if the matching calls were invoked at most N times.

    To use it, first instanciate a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked at most 1 time :
        >>> from mocki.matchers import anyCall

        >>> mock.verify(anyCall()).invoked(atMost(1))

    With one call invoked :
        >>> mock('1stCall')

        >>> mock.verify(anyCall()).invoked(atMost(1))

    With 2 calls invoked :
        >>> mock('2ndCall')

        >>> mock.verify(anyCall()).invoked(atMost(1))
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
          [1] theMock('1stCall')
          [2] theMock('2ndCall')

    """
    def __init__(self, nTimes):
        self.nTimes = nTimes

    def __call__(self, calls):
        return len(calls) <= self.nTimes

    def __repr__(self):
        """This expectation's representation :
            >>> expectation = AtMostExpectation(1)

            >>> repr(expectation)
            'atMost(1)'

        """
        return '%s(%r)' % (atMost.__name__, self.nTimes)

def atMostOnce():
    """Returns true if the matching calls were invoked at most once.

    This is a shortcut to AtMostOnceExpectation.

    """
    return AtMostOnceExpectation()

class AtMostOnceExpectation(object):
    """Returns true if the matching calls were invoked at most once.

    To use it, first instanciate a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked at most once :
        >>> from mocki.matchers import anyCall

        >>> mock.verify(anyCall()).invoked(atMostOnce())

    With one call invoked :
        >>> mock('1stCall')

        >>> mock.verify(anyCall()).invoked(atMostOnce())

    With 2 calls invoked :
        >>> mock('2ndCall')

        >>> mock.verify(anyCall()).invoked(atMostOnce())
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
          [1] theMock('1stCall')
          [2] theMock('2ndCall')

    """
    def __call__(self, calls):
        return len(calls) <= 1

    def __repr__(self):
        """This expectation's representation :
            >>> expectation = AtMostOnceExpectation()

            >>> repr(expectation)
            'atMostOnce()'

        """
        return '%s()' % atMostOnce.__name__

def between(nTimes, mTimes):
    """Returns true if the matching calls were invoked between N and M times.

    This is a shortcut to BetweenExpectation.

    """
    return BetweenExpectation(nTimes, mTimes)

class BetweenExpectation(object):
    """Returns true if the matching calls were invoked between N and M times.

    To use it, first instanciate a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked between 1 and 3 times :
        >>> from mocki.matchers import anyCall

        >>> mock.verify(anyCall()).invoked(between(1, 3))
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    With one call invoked :
        >>> mock('1stCall')

        >>> mock.verify(anyCall()).invoked(between(1, 3))

    With 2 calls invoked :
        >>> mock('2ndCall')

        >>> mock.verify(anyCall()).invoked(between(1, 3))

    With 3 calls invoked :
        >>> mock('3rdCall')

        >>> mock.verify(anyCall()).invoked(between(1, 3))

    With 4 calls invoked :
        >>> mock('4thCall')

        >>> mock.verify(anyCall()).invoked(between(1, 3))
        Traceback (most recent call last):
        ...
        AssertionError: Found 4 matching calls invoked from theMock up to now :
          [1] theMock('1stCall')
          [2] theMock('2ndCall')
          [3] theMock('3rdCall')
          [4] theMock('4thCall')

    """
    def __init__(self, nTimes, mTimes):
        self.nTimes, self.mTimes = nTimes, mTimes

    def __call__(self, calls):
        return len(calls) >= self.nTimes and len(calls) <= self.mTimes

    def __repr__(self):
        """This expectation's representation :
            >>> expectation = BetweenExpectation(1, 3)

            >>> repr(expectation)
            'between(1, 3)'

        """
        return '%s(%r, %r)' % (between.__name__, self.nTimes, self.mTimes)

def exactly(nTimes):
    """Returns true if the matching calls were invoked exactly N times.

    This is a shortcut to ExactlyExpectation.

    """
    return ExactlyExpectation(nTimes)

class ExactlyExpectation(object):
    """Returns true if the matching calls were invoked exactly N times.

    To use it, first instanciate a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked exactly 1 time :
        >>> from mocki.matchers import anyCall

        >>> mock.verify(anyCall()).invoked(exactly(1))
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    With one call invoked :
        >>> mock('1stCall')

        >>> mock.verify(anyCall()).invoked(exactly(1))

    With 2 calls invoked :
        >>> mock('2ndCall')

        >>> mock.verify(anyCall()).invoked(exactly(1))
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
          [1] theMock('1stCall')
          [2] theMock('2ndCall')

    """
    def __init__(self, nTimes):
        self.nTimes = nTimes

    def __call__(self, calls):
        return len(calls) == self.nTimes

    def __repr__(self):
        """This expectation's representation :
            >>> expectation = ExactlyExpectation(1)

            >>> repr(expectation)
            'exactly(1)'

        """
        return '%s(%r)' % (exactly.__name__, self.nTimes)

def never():
    """Returns true if the matching calls were never invoked.

    This is a shortcut to NeverExpectation.

    """
    return NeverExpectation()

class NeverExpectation(object):
    """Returns true if the matching calls were never invoked.

    To use it, first instanciate a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was never invoked :
        >>> from mocki.matchers import anyCall

        >>> mock.verify(anyCall()).invoked(never())

    With one call invoked :
        >>> mock('1stCall')

        >>> mock.verify(anyCall()).invoked(never())
        Traceback (most recent call last):
        ...
        AssertionError: Found one matching call invoked from theMock up to now :
          [1] theMock('1stCall')

    """
    def __call__(self, calls):
        return len(calls) == 0

    def __repr__(self):
        """This expectation's representation :
            >>> expectation = NeverExpectation()

            >>> repr(expectation)
            'never()'

        """
        return '%s()' % never.__name__

def once():
    """Returns true if the matching calls were invoked once.

    This is a shortcut to OnceExpectation.

    """
    return OnceExpectation()

class OnceExpectation(object):
    """Returns true if the matching calls were invoked once.

    To use it, first instanciate a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked once :
        >>> from mocki.matchers import anyCall

        >>> mock.verify(anyCall()).invoked(once())
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    With one call invoked :
        >>> mock('1stCall')

        >>> mock.verify(anyCall()).invoked(once())

    """
    def __call__(self, calls):
        return len(calls) == 1

    def __repr__(self):
        """This expectation's representation :
            >>> expectation = OnceExpectation()

            >>> repr(expectation)
            'once()'

        """
        return '%s()' % once.__name__
