import mock


class Registry(object):
    """
    A registry for mocks.
    """
    def __init__(self, specification):
        self._mocks = {}
        self._patches = []
        for name, kwargs in specification.iteritems():
            patch = mock.patch(name=name, **kwargs)
            self._patches.append(patch)


    @classmethod
    def forTestCase(cls, testCase, specification=None):
        """
        Creates a registry for this test case.

        Immediately starts this registry and schedules it to be cleaned up.
        """
        if specification is None:
            specification = testCase.mockSpecification
        registry = cls(specification)
        registry.start()
        testCase.addCleanup(registry.stop)
        return registry


    def start(self):
        """
        Starts the registry, putting mocks into effect.
        """
        for p in self._patches:
            m = p.start()
            self._mocks[m._mock_name] = m


    def stop(self):
        """
        Stops the registry, cleaning up existing mocks.
        """
        self._mocks = {}
        for p in self._patches:
            p.stop()


    def __getitem__(self, key):
        return self._mocks[key]
