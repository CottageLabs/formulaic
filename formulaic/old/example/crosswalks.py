class Transform:
    source = None
    target = None
    mapping = []
    errors = []

    def transform(self, source):
        pass

    def map_errors(self, validation_result):
        pass

class Transformer:
    def transform(self, source):
        pass

class SerialiseSubject(Transformer):
    def transform(self, source):
        return source.scheme + ":" + source.value

class UnserialiseSubject(Transformer):
    def transform(self, source):
        scheme, value = source.split(":")
        return {"scheme": scheme, "value": value}

class ObjectToForm(Transform):

    source = Top
    target = Form

    mapping = [
        {"source": Top.ID, "target": Form.ID, "transform": None},
        (Top.Keywords, Form.Keywords, None),
        (Top.Subject, Form.FormSubject, SerialiseSubject),
        (Top.Record.Title, Form.Title, None),
        (Top.Record.Authors, Form.Authors, None)
    ]

    errors = [
        {"source": Top.ID, "code": Required, "target": Form.ID, "transform": None},
        {"source": Top.ID, "code": UUIDIncorrectLength, "target": Form.ID, "transform": None},
    ]

class FormToObject(Transform):
    source = Form
    target = Top

    mapping = [
        (Form.ID, Top.ID, None),
        (Form.Keywords, Top.Keywords, None),
        (Form.FormSubject, Top.Subject, UnserialiseSubject),
        (Form.Title, Top.Record.Title, None),
        (Form.Authors, Top.Record.Authors, None)
    ]

    errors = [
        (Form.ID, UUIDIncorrectLength, Top.ID, None)
    ]