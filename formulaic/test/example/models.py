from formulaic.lib import dates
from formulaic.objects import FormulaicObject
from formulaic.test.example.structs import Journal as JournalStruct, BibJSON as JournalBibJSONStruct
import uuid

class JournalData(FormulaicObject):
    struct = JournalStruct()

class JournalBibJSONData(FormulaicObject):
    struct = JournalBibJSONStruct()
    silent_prune = False
    allow_other_fields = False
    apply_structure_on_init = False
    check_required_on_init = False
    check_required_on_set = True
    by_reference = True


class Journal:
    def __init__(self, raw=None):
        self._data = JournalData(raw)
        self._struct:JournalStruct = self._data.struct

    @property
    def data(self):
        return self._data.data

    @property
    def has_apc(self):
        return self._data.get(self._struct.bibjson.apc.has_apc)

    @property
    def id(self):
        return self._data.get(self._struct.id)

    @id.setter
    def id(self, value):
        self._data.set(self._struct.id, value)

    def set_id(self, value):
        """Set the ID of the journal."""
        if value is None:
            value = uuid.uuid4().hex
        self.id = value

    @property
    def created_date(self):
        return self._data.get(self._struct.created_date)

    @property
    def created_timestamp(self):
        return self._data.get(self._struct.created_date)

    @created_date.setter
    def created_date(self, value):
        self._data.set(self._struct.created_date, value)

    def set_created(self, value=None):
        """Set the created date of the journal."""
        if value is None:
            value = dates.now_str()
        self.created_date = value

    def add_note(self, note, date=None, id=None, author_id=None):
        """Add a note to the journal."""
        if date is None:
            date = dates.now_str()
        obj = {"date": date, "note": note, "id": id, "author_id": author_id}
        self._data.delete_from_list(self._struct.admin.notes, matchsub=obj)
        if id is None:
            id = uuid.uuid4().hex
        self._data.add_to_list(self._struct.admin.notes, obj)

    def remove_note(self, note):
        """Remove a note from the journal by its ID."""
        self._data.delete_from_list(self._struct.admin.notes, matchsub=note)

    def remove_notes(self):
        """Remove all notes from the journal."""
        self._data.delete(self._struct.admin.notes)

    def bibjson(self):
        """Return the bibjson structure of the journal."""
        bj = self._data.get(self._struct.bibjson)
        if bj is None:
            self._data.set(self._struct.bibjson, {})
            bj = self._data.get(self._struct.bibjson)
        return JournalBibJSON(bj)

class JournalBibJSON:

    def __init__(self, raw=None):
        self._data = JournalBibJSONData(raw)
        self._struct:JournalBibJSONStruct = self._data.struct

    @property
    def data(self):
        return self._data.data

    @property
    def alternative_title(self):
        return self._data.get(self._struct.alternative_title)