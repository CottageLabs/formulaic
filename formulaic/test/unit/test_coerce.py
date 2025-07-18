from unittest import TestCase

from formulaic import coerce
from formulaic.core import Field

class TestCoerce(TestCase):
    def test_unicode_coerce(self):
        class TestField(Field):
            coerce = [coerce.Unicode]

        cfn = coerce.Unicode()
        res = cfn.coerce("test", TestField())
        assert res == "test"

        res = cfn.coerce(123, TestField())
        assert res == "123"

        res = cfn.coerce("", TestField())
        assert res == ""

        res = cfn.coerce(None, TestField())
        assert res is None
