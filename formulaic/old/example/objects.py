class FormulaicObject:
    struct = None

    def __init__(self, data):
        self.data = data

    def set(self, field):
        pass

    def get(self, field):
        pass

    def validate(self):
        self.struct.validate(self.data)


class MyDataObject(FormulaicObject):
    struct = Top

class MyForm(FormulaicObject):
    struct = Form

obj = MyDataObject(OBJECT_DATA)
crosswalk = ObjectToForm()
form = crosswalk.transform(obj)