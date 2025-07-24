from unittest import TestCase

from formulaic.core import Field, REQUIRED, OPTIONAL, REPEATABLE, SINGLE, DUPLICABLE, UNIQUE
from formulaic import coerce

class FieldA(Field):
    name = "field_a"
    coerce = [coerce.Unicode]
    allow_coerce_failure = False

    allowed_values = ["value1", "value2"]
    allowed_range = ("A", "B")
    allow_none = True
    ignore_none = False

    validators = []

class FieldB(Field):
    name = "field_b"

class TestField(TestCase):
    def test_api(self):
        f = Field(OPTIONAL, SINGLE, DUPLICABLE)

        assert f.need == OPTIONAL
        assert f.required is False
        assert f.optional is True
        assert f.multiplicity == SINGLE
        assert f.repeatable is False
        assert f.non_repeatable is True
        assert f.duplicability == DUPLICABLE
        assert f.unique is False
        assert f.duplicable is True

        assert f.path == ["_field"]

        f = Field(REQUIRED, REPEATABLE, UNIQUE)

        assert f.need == REQUIRED
        assert f.required is True
        assert f.optional is False
        assert f.multiplicity == REPEATABLE
        assert f.repeatable is True
        assert f.non_repeatable is False
        assert f.duplicability == UNIQUE
        assert f.unique is True
        assert f.duplicable is False

    def test_subclass(self):
        f = FieldA()

        assert f.name == "field_a"
        assert f.coerce == [coerce.Unicode]
        assert f.allow_coerce_failure is False
        assert f.allowed_values == ["value1", "value2"]
        assert f.allowed_range == ("A", "B")
        assert f.allow_none is True
        assert f.ignore_none is False

    def test_coherence(self):
        # coherent
        f = FieldB(check_coherence=True)

        # incoherent argument set
        with self.assertRaises(ValueError):
            f = Field(REQUIRED, SINGLE, DUPLICABLE, check_coherence=True)

        FieldB.allowed_range = (3,)
        with self.assertRaises(ValueError):
            f = FieldB(check_coherence=True)

        FieldB.allowed_range = ("A", "B", "C")
        with self.assertRaises(ValueError):
            f = FieldB(check_coherence=True)

        FieldB.allowed_range = (2, 1)
        with self.assertRaises(ValueError):
            f = FieldB(check_coherence=True)

        FieldB.allowed_range = (1, 2)
        FieldB.allowed_values = [1, 2]
        with self.assertRaises(ValueError):
            f = FieldB(check_coherence=True)

        FieldB.allowed_values = []
        FieldB.allowed_range = ()







