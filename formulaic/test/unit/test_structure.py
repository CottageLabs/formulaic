from unittest import TestCase

from formulaic import coerce, engine
from formulaic.core import Field, Structure, REQUIRED, OPTIONAL, REPEATABLE, SINGLE, DUPLICABLE, StructRef
from formulaic.lib import unity

class FieldA(Field):
    name = "field_a"
    coerce = [coerce.Unicode]
    allow_coerce_failure = True

class FieldB(Field):
    name = "field_b"
    coerce = [coerce.Unicode]
    allow_coerce_failure = True

class FieldC(Field): name = "field_c"

class NestedStructure(Structure):
    _name = "nested_structure"
    field_b = FieldB(OPTIONAL, REPEATABLE)

class TopStructure(Structure):
    _name = "top_structure"
    nested_structure = NestedStructure(REQUIRED, SINGLE)
    field_a = FieldA(OPTIONAL, SINGLE)
    field_c = FieldC(REQUIRED, SINGLE)


class TestStructure(TestCase):
    def test_one_level(self):
        data = {
            "field_b": ["value1", "value2"]
        }

        s = NestedStructure()
        engine.set_data(s.field_b, ["value4", "value5"], data)
        assert data["field_b"] == ["value4", "value5"]

    def test_nested_structure(self):
        data = {
            "field_a": "test",
            "nested_structure": {
                "field_b": ["value1", "value2"]
            }
        }

        s = TopStructure()

        assert s.field_a is not None
        assert s.nested_structure is not None
        assert s.nested_structure.field_b is not None

        engine.set_data(s.field_a, "value3", data)
        engine.set_data(s.nested_structure.field_b, ["value4", "value5"], data)

        assert data["field_a"] == "value3", data
        assert data["nested_structure"]["field_b"] == ["value4", "value5"]

    def test_multiple_instances(self):
        s1 = TopStructure()
        s2 = TopStructure()
        assert s1.nested_structure._ref.parent != s2.nested_structure._ref.parent

        s1 = TopStructure()
        s2 = NestedStructure()

        assert s1.nested_structure.field_b.path == ["nested_structure", "field_b"]
        assert s2.field_b.path == ["field_b"]

    def test_ref_api(self):
        ts = TopStructure()
        tr = ts._ref

        assert ts._name == "top_structure"
        assert tr.name == "top_structure"
        assert tr.struct == ts
        assert tr.parent is None
        assert tr.root == ts
        assert tr.path == []

        required = tr.all_required
        assert len(required) == 2
        assert "nested_structure" in [unity.name(r) for r in required]
        assert "field_c" in [unity.name(r) for r in required]

        structs = tr.structures
        assert len(structs) == 1
        assert structs[0]._name == "nested_structure"

        names = tr.all_names
        assert len(names) == 3
        assert "nested_structure" in names
        assert "field_a" in names
        assert "field_c" in names

        fields = tr.fields
        assert len(fields) == 2
        assert "field_a" in [f.name for f in fields]
        assert "field_c" in [f.name for f in fields]

        all = tr.all
        assert len(all) == 3
        assert "nested_structure" in [unity.name(e) for e in all]
        assert "field_a" in [unity.name(e) for e in all]
        assert "field_c" in [unity.name(e) for e in all]

        assert tr.by_name("field_a").name == "field_a"
        assert tr.by_name("nested_structure")._name == "nested_structure"
        assert tr.by_name("field_c").name == "field_c"
        assert tr.by_name("non_existent") is None

        field = tr.get_path("nested_structure.field_b")
        assert field.name == "field_b"

        field = tr.get_path(["nested_structure", "field_b"])
        assert field.name == "field_b"

        ns = ts.nested_structure
        nr = ns._ref

        assert nr.name == "nested_structure"
        assert nr.struct == ns
        assert nr.parent == ts
        assert nr.root == ts
        assert nr.path == ["nested_structure"]

        assert nr.need == REQUIRED
        assert nr.required is True
        assert nr.optional is False
        assert nr.multiplicity == SINGLE
        assert nr.repeatable is False
        assert nr.non_repeatable is True
        assert nr.duplicability == DUPLICABLE
        assert nr.unique is False
        assert nr.duplicable is True

        field = nr.by_name("field_b")
        assert field.name == "field_b"

        field = nr.get_path("field_b")
        assert field.name == "field_b"