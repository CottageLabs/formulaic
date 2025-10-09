from formulaic.core import Structure, REQUIRED, OPTIONAL, REPEATABLE, SINGLE, StructRef
from formulaic.objects import FormulaicObject

from formulaic.test.example import fields
from formulaic.test.example import structs


class OutgoingJournalAdminStruct(Structure):
    _name = "admin"

    in_doaj = fields.InDOAJ(OPTIONAL, SINGLE)
    ticked = fields.Ticked(OPTIONAL, SINGLE)


class OutgoingJournalStruct(Structure):
    _name = "outgoing_journal"

    id = fields.ID(OPTIONAL, SINGLE)
    created_date = fields.CreatedDate(OPTIONAL, SINGLE)
    last_updated = fields.LastUpdated(OPTIONAL, SINGLE)
    last_manual_update = fields.LastManualUpdate(OPTIONAL, SINGLE)
    es_type = fields.ESType(OPTIONAL, SINGLE)

    bibjson = structs.BibJSON(OPTIONAL, SINGLE)
    admin = OutgoingJournalAdminStruct(OPTIONAL, SINGLE)


###########################################

class OutgoingJournalData(FormulaicObject):
    struct = OutgoingJournalStruct()
    silent_prune = True


class OutgoingJournal:
    def __init__(self, raw=None):
        self._data = OutgoingJournalData(raw)
        self._struct:OutgoingJournalStruct = self._data.struct

    @property
    def data(self):
        return self._data.data

