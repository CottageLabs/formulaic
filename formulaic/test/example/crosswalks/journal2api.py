from formulaic.transform import Transform

from formulaic.test.example.structs import Journal
from formulaic.test.example.api import OutgoingJournalStruct

class Journal2OutgoingJournal(Transform):
    source = Journal()
    target = OutgoingJournalStruct()

    mapping = [
        # map all the basic properties directly
        (source.id, target.id),
        (source.created_date, target.created_date),
        (source.last_updated, target.last_updated),
        (source.last_manual_update, target.last_manual_update),
        (source.es_type, target.es_type),

        # take the bibjson as an entirity
        (source.bibjson, target.bibjson),

        # mape the two admin properties
        (source.admin.in_doaj, target.admin.in_doaj),
        (source.admin.ticked, target.admin.ticked),
    ]