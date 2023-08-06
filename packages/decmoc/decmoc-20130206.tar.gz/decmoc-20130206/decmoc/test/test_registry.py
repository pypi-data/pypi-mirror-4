from decmoc.registry import Registry
from unittest import TestCase


target = object()
realTarget = target


mockSpecification = {
    "target": {"target": "decmoc.test.test_registry.target"}
}



class RegistryTests(TestCase):
    def setUp(self):
        self.registry = Registry(mockSpecification)


    def test_roundtrip(self):
        def getTarget():
            return self.registry["target"]

        self.assertRaises(KeyError, getTarget)
        self.assertIs(target, realTarget)

        self.registry.start()
        mock = getTarget()
        self.assertIs(mock, target)

        self.registry.stop()
        self.assertRaises(getTarget)
        self.assertIs(target, realTarget)



class ForTestCaseTests(TestCase):
    mockSpecification = mockSpecification

    def test_forTestCase(self):
        self.assertEqual(len(Registry.forTestCase(self)._patches), 1)



class ForTestCaseWithoutSpecificationTests(TestCase):
    def test_noSpecification(self):
        self.assertRaises(AttributeError, Registry.forTestCase, self)


    def test_passedSpecifcation(self):
        registry = Registry.forTestCase(self, {})
        self.assertEqual(registry._patches, [])
