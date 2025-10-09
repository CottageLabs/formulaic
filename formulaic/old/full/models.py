from formulaic.core import FormulaicObject

class JournalFormulaic(FormulaicObject):
    struct = JournalStruct


class Journal:
    def __init__(self, data=None):
        self._data = JournalFormulaic(data)

    @property
    def data(self):
        return self._data.data

    @property
    def has_apc(self):
        return self._data.get(JournalStruct.JournalBibJSON.APC.HasAPC)

    @has_apc.property
    def has_apc(self, val):
        self._data.set(JournalStruct.JournalBibJSON.APC.HasAPC, val)

    @property
    def id(self):
        return self._data.get("id")

    @id.setter
    def id(self, id):
        self._data.set("id", id)


class JournalCSVFormulaic(FormulaicObject):
    struct = JournalCSVStruct


