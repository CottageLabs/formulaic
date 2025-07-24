from unittest import TestCase

from formulaic import coerce, engine
from formulaic.core import Field, Structure, REQUIRED, OPTIONAL, REPEATABLE, SINGLE, StructRef


class FieldA(Field):
    name = "field_a"
    coerce = [coerce.Unicode]
    allow_coerce_failure = True

class FieldB(Field):
    name = "field_b"
    coerce = [coerce.Unicode]
    allow_coerce_failure = True

class MockStructure(Structure):
    _name = "mock_structure"
    field_a = FieldA(REQUIRED, SINGLE)
    field_b = FieldB(OPTIONAL, REPEATABLE)

class SuperStructure(Structure):
    _name = "super_structure"
    mock_structure = MockStructure(REQUIRED, SINGLE)

class TestStructure(TestCase):
    def test_one_level(self):
        data = {
            "field_a": "test",
            "field_b": ["value1", "value2"]
        }

        s = MockStructure()
        # validate(data, MockStructure)

        engine.set_data(s.field_a, "value3", data)
        engine.set_data(s.field_b, ["value4", "value5"], data)
        #add_data(MockStructure.field_b, "value4", data)

        assert data["field_a"] == "value3", data
        assert data["field_b"] == ["value4", "value5"]

    def test_nested_structure(self):
        data = {
            "mock_structure": {
                "field_a": "test",
                "field_b": ["value1", "value2"]
            }
        }

        s = SuperStructure()
        engine.set_data(s.mock_structure.field_a, "value3", data)
        engine.set_data(s.mock_structure.field_b, ["value4", "value5"], data)

        assert data["mock_structure"]["field_a"] == "value3", data
        assert data["mock_structure"]["field_b"] == ["value4", "value5"]

    def test_multiple_instances(self):
        s1 = SuperStructure()
        s2 = SuperStructure()
        assert s1.mock_structure._ref.parent != s2.mock_structure._ref.parent

        s1 = SuperStructure()
        s2 = MockStructure()

        assert s1.mock_structure.field_a.path == ["mock_structure", "field_a"]
        assert s2.field_a.path == ["field_a"]