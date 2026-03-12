from formulaic.crosswalk.core import Crosswalk

from formulaic.test.example.structs import JournalStructure
from formulaic.test.example.api import OutgoingJournalStruct, OutgoingJournal


class Journal2OutgoingJournal(Crosswalk):
    source = JournalStructure()
    target = OutgoingJournalStruct()
    target_class = OutgoingJournal

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