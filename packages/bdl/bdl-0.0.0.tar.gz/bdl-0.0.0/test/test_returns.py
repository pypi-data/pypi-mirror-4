from bdl import returns
from unittest import TestCase

class TestReturns(TestCase):
    def test_passes_with_type(self):
        @returns(dict)
        def test_func():
            return {}
        
        self.assertEquals(test_func(), {})

    def test_passes_with_example(self):
        @returns({})
        def test_func():
            return {}

        self.assertEquals(test_func(), {})

    def test_raises_type_error(self):
        @returns(dict)
        def test_func():
            return []

        self.assertRaises(TypeError,
                          test_func)

        
