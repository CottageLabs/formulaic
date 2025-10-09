class Schematiser:
    def serialise(self, struct):
        pass

    def parse(self, stream):
        pass


class ESMapping(Schematiser):
    def __init__(self, field_mappings):
        self.field_mappings = field_mappings

    def serialise(self, struct):
        pass

    def parse(self, stream):
        pass


class SeamlessStruct(Schematiser):
    def serialise(self, struct):
        s = {
            "fields": {},
            "lists": {},
            "objects": [],
            "structs": {}

        }
        for field in struct._field_iterator():
            f = field["field"]
            s["fields"][f.name] = {
                "coerce": {
                    "pipeline": field.coerce_pipeline,
                    "allow_coerce_failure": field.allow_coerce_failure
                },
                "required": field["required"],
                "validate": field.validators
            }

        # and so on for lists and structs

    def parse(self, stream):
        pass
