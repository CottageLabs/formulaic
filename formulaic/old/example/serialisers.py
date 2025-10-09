class Serialiser:
    def serialise(self, formulaic_object):
        pass

    def parse(self, stream, formulaic_class):
        pass


class JSONSerialiser(Serialiser):
    def serialise(self, formulaic_object):
        return json.dumps(formulaic_object.data)

    def parse(self, stream, formulaic_class):
        return formulaic_class(json.loads(stream))

class FormData(Serialiser):
    def serialise(self, formulaic_object):
        formdata = {}
        for field_ref, value in formulaic_object.walk_leaf_nodes():
            key = ".".join(field_ref.path)
            formdata[key] = value

    def parse(self, stream, formulaic_class):
        pass
