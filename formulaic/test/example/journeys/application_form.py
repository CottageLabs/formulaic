from formulaic.serialise.json import JSONSerialiser
from formulaic.test.example.data import JOURNAL_SOURCE
from formulaic.test.example.models import Journal
from formulaic.test.example.crosswalks.journal2form import Journal2Form

journal = Journal(JOURNAL_SOURCE)
xwalk = Journal2Form()
form_data = xwalk.transform(journal)
print(form_data)