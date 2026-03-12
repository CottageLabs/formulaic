from formulaic.serialise.json import JSONSerialiser
from formulaic.test.example.data import JOURNAL_SOURCE
from formulaic.test.example.models import Journal

journal = Journal(JOURNAL_SOURCE)
serialiser = JSONSerialiser()
out = serialiser.data_to_string(journal, indent=4, sort_keys=True)
print(out)