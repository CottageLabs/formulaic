from formulaic.serialise.json import JSONSerialiser
from formulaic.test.example.api import OutgoingJournal
from formulaic.test.example.data import JOURNAL_SOURCE
from formulaic.test.example.models import Journal
from formulaic.test.example.crosswalks.journal2api import Journal2OutgoingJournal

journal = Journal(JOURNAL_SOURCE)
xwalk = Journal2OutgoingJournal()
outgoing_journal = xwalk.transform(journal)
serialiser = JSONSerialiser()
out = serialiser.to_string(outgoing_journal, indent=2, sort_keys=True)
print(out)
