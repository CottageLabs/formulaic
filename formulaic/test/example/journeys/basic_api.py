from formulaic.test.example.api import OutgoingJournal
from formulaic.test.example.data import JOURNAL_SOURCE
from formulaic.test.example.models import Journal
from formulaic.test.example.crosswalks.journal2api import Journal2OutgoingJournal

journal = Journal(JOURNAL_SOURCE)
xwalk = Journal2OutgoingJournal()
api_data = xwalk.transform(journal.data)
outgoing_journal = OutgoingJournal(api_data)

print(outgoing_journal.data)
