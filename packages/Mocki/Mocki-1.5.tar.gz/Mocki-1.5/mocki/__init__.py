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

"""An easy-to-use but full featured mocking library for Python.

Here is a short example showing how to start working with Mocki :
    >>> mock = Mock('theMock')

    >>> mock.verifyCall(1, 2, 3, x=7, y=8, z=9).invokedOnce()
    Traceback (most recent call last):
    ...
    AssertionError: No call invoked from theMock up to now.

    >>> mock(1, 2, 3, x=7, y=8, z=9)

    >>> mock.verifyCall(1, 2, 3, x=7, y=8, z=9).invokedOnce()

"""
import collections, inspect, threading

class Mock(object):
    """A mock is a callable object that is able to track any call invoked from
    it and that will automatically provide on-fly generated mock members from
    each non existing member accessed.

    To use it, first instanciate a mock giving it a name, then invoke some calls
    from it, with or without args and kwargs :
        >>> mock = Mock('theMock')

        >>> mock()
        >>> mock(1, 2, 3)
        >>> mock(x=7, y=8, z=9)
        >>> mock(1, 2, 3, x=7, y=8, z=9)

    Now, we can ask to verify whether or not a given call was invoked from it :
        >>> from mocki.expectations import once
        >>> from mocki.matchers import call

        >>> mock.verify(call(1, 2, 3, x=7, y=8, z=9)).invoked(once())

    In case of verification failure, an assertion error will be raised with a
    debugging-friendly message indicating the problem :
        >>> mock.verify(call(7, 8, 9, x=1, y=2, z=3)).invoked(once())
        Traceback (most recent call last):
        ...
        AssertionError: Found no matching call invoked from theMock up to now :
           1  theMock()
           2  theMock(1, 2, 3)
           3  theMock(x=7, y=8, z=9)
           4  theMock(1, 2, 3, x=7, y=8, z=9)

    You can also invoke some calls from its mock members :
        >>> mock.method()
        >>> mock.otherMethod(1, 2, 3)
        >>> mock.method(x=7, y=8, z=9)
        >>> mock.otherMethod(1, 2, 3, x=7, y=8, z=9)

    Now, we can ask to verify whether or not a given call was invoked from any
    of its mock members :
        >>> mock.otherMethod.verify(call(1, 2, 3, x=7, y=8, z=9)).invoked(once())

    In case of verification failure, an assertion error will be raised with a
    debugging-friendly message indicating the problem :
        >>> mock.otherMethod.verify(call(7, 8, 9, x=1, y=2, z=3)).invoked(once()) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        AssertionError: Found no matching call invoked from theMock.otherMethod up to now :
           6  theMock.otherMethod(1, 2, 3)
           8  theMock.otherMethod(1, 2, 3, x=7, y=8, z=9)

    Actually, since mock members are mocks themselves, everything possible on
    mocks is also possible on their members. And everything possible on their
    members is also possible their members members, and so on...

    Note that the following member names are reserved and cannot be used as mock
    member names : verify*, on*.

    """
    def __init__(self, name):
        self._name = name

        self._invocations = []
        self._verifiedIndices = []
        self._stub = lambda call: None

        self._mockMemberLock = threading.RLock()

        def loadMatchersShortcuts():
            import mocki.matchers

            class MatcherShortcut(object):
                def __init__(self, method, matcherType):
                    self.method = method
                    self.matcherType = matcherType

                def __call__(self, *args, **kwargs):
                    return self.method(self.matcherType(*args, **kwargs))

            for matcherTypeName in filter(lambda matcherTypeName: matcherTypeName.endswith('Matcher'), dir(mocki.matchers)):
                setattr(self, 'verify%s' % matcherTypeName[:-len('Matcher')], MatcherShortcut(self.verify, getattr(mocki.matchers, matcherTypeName)))
                setattr(self, 'on%s' % matcherTypeName[:-len('Matcher')], MatcherShortcut(self.on, getattr(mocki.matchers, matcherTypeName)))

        loadMatchersShortcuts()

    def __call__(self, *args, **kwargs):
        invocation = CallInvocation(self, Call(*args, **kwargs))
        self._invocations.append(invocation)
        return self._stub(invocation.call)

    def __getattr__(self, mockMemberName):
        with self._mockMemberLock:
            if mockMemberName not in dir(self):
                member = Mock('%s.%s' % (self._name, mockMemberName))
                member._invocations = self._invocations
                member._verifiedIndices = self._verifiedIndices
                setattr(self, mockMemberName, member)

            return getattr(self, mockMemberName)

    def verify(self, matcher):
        """Verifies whether or not the given matching calls were invoked.

        To use it, first instanciate a mock to verify :
            >>> mock = Mock('theMock')

        If we ask to verify whether or not a 2nd call was invoked from the mock,
        an assertion error will be raised with a debugging-friendly message
        indicating that no call has been invoked from it up to now :
            >>> from mocki.expectations import once
            >>> from mocki.matchers import call

            >>> mock.verify(call('2ndCall')).invoked(once())
            Traceback (most recent call last):
            ...
            AssertionError: No call invoked from theMock up to now.

        Or, you may prefer to write the same statement in a shorter manner :
            >>> mock.verifyCall('2ndCall').invokedOnce()
            Traceback (most recent call last):
            ...
            AssertionError: No call invoked from theMock up to now.

        Now, invoke some calls from the mock :
            >>> mock('1stCall')
            >>> mock('2ndCall')
            >>> mock('1stCall')

        If we ask again to verify whether or not the 2nd call was invoked, no
        more assertion error will be raised, which means that the 2nd call was
        invoked as expected :
            >>> mock.verify(call('2ndCall')).invoked(once())

        Of course, if we ask the contrary, an assertion error will be raised :
            >>> from mocki.expectations import never

            >>> mock.verify(call('2ndCall')).invoked(never())
            Traceback (most recent call last):
            ...
            AssertionError: Found one matching call invoked from theMock up to now :
               1  theMock('1stCall')
              [2] theMock('2ndCall')
               3  theMock('1stCall')

        What is interesting here is the debugging-friendly message attached to
        the assertion error. It clearly shows us which calls were invoked from
        the mock up to now, and among them, which ones are matching with the
        verification statement. Here are some other examples :
            >>> mock.verify(call('1stCall')).invoked(once())
            Traceback (most recent call last):
            ...
            AssertionError: Found 2 matching calls invoked from theMock up to now :
              [1] theMock('1stCall')
               2  theMock('2ndCall')
              [3] theMock('1stCall')

            >>> mock.verify(call('3rdCall')).invoked(once())
            Traceback (most recent call last):
            ...
            AssertionError: Found no matching call invoked from theMock up to now :
               1  theMock('1stCall')
               2  theMock('2ndCall')
               3  theMock('1stCall')

        Sometimes, it can be very useful to verify that some calls were invoked
        in a particular order. This is done with in order verifications.

        An important thing to known about in order verifications is that we can
        only make these verifications on mocks that share at least one parent.
        Actually, this is not a huge problem, since we can safely instanciate
        mocks from other mocks :
            >>> mock = Mock('theMock')

            >>> method, otherMethod, anotherMethod = mock.method, mock.otherMethod, mock.anotherMethod

        If we ask to verify whether or not a 2nd call was invoked from one of
        these mocks, an assertion error will be raised with a debugging-friendly
        message indicating that no call has been invoked from it up to now :
            >>> otherMethod.verify(call('2ndCall')).invokedInOrder()
            Traceback (most recent call last):
            ...
            AssertionError: No call invoked from theMock.otherMethod up to now.

        Now, invoke some calls from these mocks :
            >>> method('1stCall')
            >>> otherMethod('2ndCall')
            >>> method('1stCall')

        If we ask again to verify whether or not the 2nd call was invoked, no
        more assertion error will be raised, which means that the 2nd call was
        invoked as expected :
            >>> otherMethod.verify(call('2ndCall')).invokedInOrder()

        But, if we now make this verification twice, an assertion error will be
        raised again, since no other 2nd call was invoked :
            >>> otherMethod.verify(call('2ndCall')).invokedInOrder()
            Traceback (most recent call last):
            ...
            AssertionError: Found one matching call invoked from theMock.otherMethod up to now, but not in order :
               1  theMock.method('1stCall')
            X [2] theMock.otherMethod('2ndCall')
               3  theMock.method('1stCall')

        What is interesting here is the debugging-friendly message attached to
        the assertion error. It clearly shows us which calls were invoked from
        the mock up to now, and among them, which ones were already verified and
        which ones are matching with the verification statement. Here are some
        other examples :
            >>> method.verify(call('1stCall')).invokedInOrder()

            >>> method.verify(call('1stCall')).invokedInOrder()
            Traceback (most recent call last):
            ...
            AssertionError: Found 2 matching calls invoked from theMock.method up to now, but not in order :
              [1] theMock.method('1stCall')
            X  2  theMock.otherMethod('2ndCall')
            X [3] theMock.method('1stCall')

            >>> method.verify(call('3rdCall')).invokedInOrder()
            Traceback (most recent call last):
            ...
            AssertionError: Found no matching call invoked from theMock.method up to now :
               1  theMock.method('1stCall')
            X  2  theMock.otherMethod('2ndCall')
            X  3  theMock.method('1stCall')

            >>> anotherMethod.verify(call('3rdCall')).invokedInOrder()
            Traceback (most recent call last):
            ...
            AssertionError: No call invoked from theMock.anotherMethod up to now.

        """
        class OnMockCallVerifier(object):
            def __init__(self, mock, matcher):
                self.mock = mock
                self.matcher = matcher

                def loadExpectationsShortcuts():
                    import mocki.expectations

                    class ExpectationShortcut(object):
                        def __init__(self, method, expectationType):
                            self.method = method
                            self.expectationType = expectationType

                        def __call__(self, *args, **kwargs):
                            return self.method(self.expectationType(*args, **kwargs))

                    for expectationTypeName in filter(lambda expectationTypeName: expectationTypeName.endswith('Expectation'), dir(mocki.expectations)):
                        setattr(self, 'invoked%s' % expectationTypeName[:-len('Expectation')], ExpectationShortcut(self.invoked, getattr(mocki.expectations, expectationTypeName)))

                loadExpectationsShortcuts()

            def invoked(self, expectation):
                IndexedCallInvocation = collections.namedtuple('IndexedCallInvocation', 'index invocation')

                def getMockInvocations():
                    def iterateMockInvocations():
                        for index, invocation in enumerate(self.mock._invocations):
                            if invocation.mock is self.mock:
                                yield IndexedCallInvocation(index, invocation)

                    return list(iterateMockInvocations())

                def getMatchingMockInvocations():
                    def iterateMatchingMockInvocations():
                        for index, invocation in enumerate(self.mock._invocations):
                            if invocation.mock is self.mock and self.matcher(invocation.call):
                                yield IndexedCallInvocation(index, invocation)

                    return list(iterateMatchingMockInvocations())

                def buildInvocationsHistory():
                    def iterateInvocationsHistoryLines():
                        for item in getMockInvocations():
                            if item in getMatchingMockInvocations():
                                yield '  [%r] %s' % (item.index+1, str(item.invocation))
                            else:
                                yield '   %r  %s' % (item.index+1, str(item.invocation))

                    return '\n'.join(iterateInvocationsHistoryLines())

                if not expectation(getMatchingMockInvocations()):
                    if len(getMockInvocations()) == 0:
                        raise AssertionError('No call invoked from %s up to now.' % self.mock._name)
                    else:
                        if len(getMatchingMockInvocations()) == 0:
                            raise AssertionError('Found no matching call invoked from %s up to now :\n%s' % (self.mock._name, buildInvocationsHistory()))
                        elif len(getMatchingMockInvocations()) == 1:
                            raise AssertionError('Found one matching call invoked from %s up to now :\n%s' % (self.mock._name, buildInvocationsHistory()))
                        else:
                            raise AssertionError('Found %s matching calls invoked from %s up to now :\n%s' % (len(getMatchingMockInvocations()), self.mock._name, buildInvocationsHistory()))

            def invokedInOrder(self):
                IndexedCallInvocation = collections.namedtuple('IndexedCallInvocation', 'index invocation')

                def getAllInvocations():
                    def iterateAllInvocations():
                        for index, invocation in enumerate(self.mock._invocations):
                            yield IndexedCallInvocation(index, invocation)

                    return list(iterateAllInvocations())

                def getAllVerifiedInvocations():
                    def iterateAllInvocations():
                        for index, invocation in enumerate(self.mock._invocations):
                            if index in self.mock._verifiedIndices:
                                yield IndexedCallInvocation(index, invocation)

                    return list(iterateAllInvocations())

                def getMockInvocations():
                    def iterateMockInvocations():
                        for index, invocation in enumerate(self.mock._invocations):
                            if invocation.mock is self.mock:
                                yield IndexedCallInvocation(index, invocation)

                    return list(iterateMockInvocations())

                def getMatchingMockInvocations():
                    def iterateMatchingMockInvocations():
                        for index, invocation in enumerate(self.mock._invocations):
                            if invocation.mock is self.mock and self.matcher(invocation.call):
                                yield IndexedCallInvocation(index, invocation)

                    return list(iterateMatchingMockInvocations())

                def getInOrderMatchingMockInvocations():
                    def iterateInOrderMatchingMockInvocations():
                        lastVerificationInOrderIndex = max(self.mock._verifiedIndices) if len(self.mock._verifiedIndices) > 0 else 0
                        for index, invocation in enumerate(self.mock._invocations):
                            if invocation.mock is self.mock and self.matcher(invocation.call) and index > lastVerificationInOrderIndex:
                                yield IndexedCallInvocation(index, invocation)

                    return list(iterateInOrderMatchingMockInvocations())

                def buildInvocationsHistory():
                    def iterateInvocationsHistoryLines():
                        for item in getAllInvocations():
                            if item in getMatchingMockInvocations():
                                if item in getAllVerifiedInvocations():
                                    yield 'X [%r] %s' % (item.index+1, str(item.invocation))
                                else:
                                    yield '  [%r] %s' % (item.index+1, str(item.invocation))
                            else:
                                if item in getAllVerifiedInvocations():
                                    yield 'X  %r  %s' % (item.index+1, str(item.invocation))
                                else:
                                    yield '   %r  %s' % (item.index+1, str(item.invocation))

                    return '\n'.join(iterateInvocationsHistoryLines())

                if len(getInOrderMatchingMockInvocations()) > 0:
                    self.mock._verifiedIndices.append(getInOrderMatchingMockInvocations()[0].index)
                else:
                    if len(getMockInvocations()) == 0:
                        raise AssertionError('No call invoked from %s up to now.' % self.mock._name)
                    else:
                        if len(getMatchingMockInvocations()) == 0:
                            raise AssertionError('Found no matching call invoked from %s up to now :\n%s' % (self.mock._name, buildInvocationsHistory()))
                        elif len(getMatchingMockInvocations()) == 1:
                            raise AssertionError('Found one matching call invoked from %s up to now, but not in order :\n%s' % (self.mock._name, buildInvocationsHistory()))
                        else:
                            raise AssertionError('Found %s matching calls invoked from %s up to now, but not in order :\n%s' % (len(getMatchingMockInvocations()), self.mock._name, buildInvocationsHistory()))

        return OnMockCallVerifier(self, matcher)

    def on(self, matcher):
        """Stubs this mock on invocation to the given matching calls.

        To use it, first instanciate a mock, then stub it as desired, e.g. to
        return a given value on invocation to the given matching calls :
            >>> from mocki.matchers import anyCall
            >>> from mocki.stubs import returnValue

            >>> mock = Mock('theMock')

            >>> mock.on(anyCall()).then(returnValue('value'))

        Or, you may prefer to write the same statement in a shorter manner :
            >>> mock.onAnyCall().thenReturnValue('value')

        Now, any matching invocation will return this given value :
            >>> mock('1stCall')
            'value'

            >>> mock('2ndCall')
            'value'

        Sometimes, it can be very useful to override a global stub with a more
        specific one. This is simply done by defining a new specific stub over
        the already existing global one. E.g., here is how to define a new
        specific stub for the 2nd call :
            >>> from mocki.matchers import call

            >>> mock.on(call('2ndCall')).then(returnValue('otherValue'))

        Now, the 2nd call will use the new specific stub we defined, even if the
        global one is still existing and matching with it :
            >>> mock('1stCall')
            'value'

            >>> mock('2ndCall')
            'otherValue'

        """
        class CallStubber(object):
            def __init__(self, mock, matcher):
                self.mock = mock
                self.matcher = matcher

                def loadStubsShortcuts():
                    import mocki.stubs

                    class StubShortcut(object):
                        def __init__(self, method, stubType):
                            self.method = method
                            self.stubType = stubType

                        def __call__(self, *args, **kwargs):
                            return self.method(self.stubType(*args, **kwargs))

                    for stubTypeName in filter(lambda stubTypeName: stubTypeName.endswith('Stub'), dir(mocki.stubs)):
                        setattr(self, 'then%s' % stubTypeName[:-len('Stub')], StubShortcut(self.then, getattr(mocki.stubs, stubTypeName)))

                loadStubsShortcuts()

            def then(self, stub):
                class StubDecorator(object):
                    def __init__(self, stub, matcher, decoratedStub):
                        self.stub = stub
                        self.matcher = matcher
                        self.decoratedStub = decoratedStub

                    def __call__(self, call):
                        if self.matcher(call):
                            return self.stub(call)
                        else:
                            return self.decoratedStub(call)

                self.mock._stub = StubDecorator(stub, self.matcher, self.mock._stub)

        return CallStubber(self, matcher)

class AutoMocks(object):
    """Used as function decorator to automatically provide mocks.

    To use it, you need to put this decorator in front of your function and tag
    the corresponding arguments by setting their default values to Mock :
        >>> from mocki.expectations import once
        >>> from mocki.matchers import anyCall

        >>> @AutoMocks
        ... def testSomething(a, b, c, x=7, y=8, z=9, oneMock=Mock, anotherMock=Mock):
        ...     anotherMock.verify(anyCall()).invoked(once())

    Now, any argument having its default value set to Mock will automatically
    get a new mock instance each time this function is invoked :
        >>> testSomething(1, 2, 3, x=7, y=8, z=9)
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from anotherMock up to now.

    """
    def __new__(cls, func):
        def decoratedFunc(*args, **kwargs):
            def populateKwargsWithAutoMocks(**kwargs):
                populatedKwargs = dict(kwargs)

                for name, defaultValue in zip(reversed(inspect.getargspec(func).args), reversed(inspect.getargspec(func).defaults)):
                    if defaultValue is Mock:
                        populatedKwargs[name] = Mock(name)

                return populatedKwargs

            func(*kwargs, **populateKwargsWithAutoMocks(**kwargs))

        # Required for the nose autodiscovery feature to work.
        decoratedFunc.__name__ = func.__name__

        return decoratedFunc

class Patch(object):
    """Used in with statements to temporary replace static members.

    To use it, you first need a static member to mock :
        >>> class Parent(object):
        ...     @classmethod
        ...     def staticMethod(cls):
        ...         return 'value'

    You also need a value that will temporary replace this static member within
    the with statement, e.g. a mock :
        >>> mock = Mock('theMock')

    Before the with statement, the static member behaves normally :
        >>> Parent.staticMethod()
        'value'

    Within the with statement, the static member lost its normal behavior. It is
    temporary replaced by the provided mock :
        >>> from mocki.expectations import once
        >>> from mocki.matchers import anyCall

        >>> with Patch(Parent, 'staticMethod', mock):
        ...     Parent.staticMethod.verify(anyCall()).invoked(once())
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    After the with statement, the static member recovers its normal behavior :
        >>> Parent.staticMethod()
        'value'

    """
    def __init__(self, parent, staticMemberName, newValue):
        self.parent, self.staticMemberName, self.newValue = parent, staticMemberName, newValue

    def __enter__(self):
        self.oldValue = getattr(self.parent, self.staticMemberName)
        setattr(self.parent, self.staticMemberName, self.newValue)

    def __exit__(self, type, value, traceback):
        setattr(self.parent, self.staticMemberName, self.oldValue)

class Call(collections.namedtuple('Call', 'args kwargs')):
    """A call with its args and kwargs.

    """
    def __new__(cls, *args, **kwargs):
        return super(Call, cls).__new__(cls, args, kwargs)

    def __hash__(self):
        return hash(self.args) + hash(tuple(self.kwargs.items()))

    def __repr__(self):
        """This call's representation :
            >>> repr(Call())
            'Call()'

            >>> repr(Call(1, 2.0, '300'))
            "Call(1, 2.0, '300')"

            >>> repr(Call(x=7, y=8.0, z='900'))
            "Call(x=7, y=8.0, z='900')"

            >>> repr(Call(1, 2.0, '300', x=7, y=8.0, z='900'))
            "Call(1, 2.0, '300', x=7, y=8.0, z='900')"

        """
        def getArgsAsCsv():
            return ", ".join(map(repr, self.args))

        def getKwargsAsCsv():
            return ", ".join(map(lambda kwarg: '%s=%r' % kwarg, sorted(self.kwargs.items())))

        if len(self.args) == 0 and len(self.kwargs) == 0:
            return 'Call()'
        elif len(self.kwargs) == 0:
            return 'Call(%s)' % getArgsAsCsv()
        elif len(self.args) == 0:
            return 'Call(%s)' % getKwargsAsCsv()
        else:
            return 'Call(%s, %s)' % (getArgsAsCsv(), getKwargsAsCsv())

class CallInvocation(collections.namedtuple('CallInvocation', 'mock call')):
    """A call invocation represents a call invoked on a particular mock.

    """
    def __str__(self):
        """Returns a pretty string representing this call invocation :
            >>> mock = Mock('theMock')

            >>> print(CallInvocation(mock, Call()))
            theMock()

            >>> print(CallInvocation(mock, Call(1, 2.0, '300')))
            theMock(1, 2.0, '300')

            >>> print(CallInvocation(mock, Call(x=7, y=8.0, z='900')))
            theMock(x=7, y=8.0, z='900')

            >>> print(CallInvocation(mock, Call(1, 2.0, '300', x=7, y=8.0, z='900')))
            theMock(1, 2.0, '300', x=7, y=8.0, z='900')

        """
        def getArgsAsCsv():
            return ", ".join(map(repr, self.call.args))

        def getKwargsAsCsv():
            return ", ".join(map(lambda kwarg: '%s=%r' % kwarg, sorted(self.call.kwargs.items())))

        if len(self.call.args) == 0 and len(self.call.kwargs) == 0:
            return '%s()' % self.mock._name
        elif len(self.call.kwargs) == 0:
            return '%s(%s)' % (self.mock._name, getArgsAsCsv())
        elif len(self.call.args) == 0:
            return '%s(%s)' % (self.mock._name, getKwargsAsCsv())
        else:
            return '%s(%s, %s)' % (self.mock._name, getArgsAsCsv(), getKwargsAsCsv())
